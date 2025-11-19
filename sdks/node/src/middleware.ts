/**
 * AgentEval Middleware for Node.js/Next.js
 * 
 * Drop-in middleware that translates AgentEval standard format
 * to your agent's API format and back.
 * 
 * Usage:
 *   import { createAgentEvalMiddleware } from '@agent-eval/node'
 *   
 *   app.post('/api/agenteval', createAgentEvalMiddleware({
 *     targetEndpoint: '/api/unifiedchat',
 *     parseResponse: (ndjson) => ({ output, steps, cost, latency })
 *   }))
 */

export interface AgentEvalRequest {
  query: string;
  context?: {
    route?: string;
    userId?: string;
    conversationId?: string;
    history?: any[];
    [key: string]: any;
  };
  enable_tracing?: boolean;
}

export interface AgentEvalStep {
  id: string;
  name: string;
  tool: string;
  parameters: any;
  output?: any;
  success: boolean;
  latency?: number;
  cost?: number;
  tokens?: number;
}

export interface AgentEvalResponse {
  session_id: string;
  output: string;
  steps: AgentEvalStep[];
  cost: number;
  latency: number;
  tokens?: number;
}

export interface MiddlewareConfig {
  /** Endpoint to forward requests to (e.g., '/api/unifiedchat') */
  targetEndpoint: string;

  /** Optional: Transform AgentEval request to your API format */
  transformRequest?: (req: AgentEvalRequest) => any;

  /** Optional: Parse your API response to AgentEval format */
  parseResponse?: (responseText: string, startTime: number) => AgentEvalResponse;

  /** Optional: Base URL for requests (defaults to current host) */
  baseUrl?: string;

  /** Optional: Default user ID for test requests (defaults to 'agenteval-test-user') */
  defaultUserId?: string;

  /** Optional: Function to get/create user ID dynamically */
  getUserId?: (req: AgentEvalRequest) => string | Promise<string>;
}

/**
 * Default Tapescope request transformer
 */
function defaultTransformRequest(req: AgentEvalRequest) {
  const timestamp = Date.now();
  return {
    message: req.query,
    userId: req.context?.userId, // Set by middleware
    conversationId: req.context?.conversationId || `eval-${timestamp}`,
    route: req.context?.route || 'orchestrator',
    history: req.context?.history || [],
  };
}

/**
 * Default Tapescope NDJSON response parser
 * Handles both pure NDJSON and SSE format (with "data: " prefix)
 */
function defaultParseResponse(ndjsonText: string, startTime: number): AgentEvalResponse {
  const lines = ndjsonText.trim().split('\n');
  const events = lines
    .filter(line => line.trim())
    .map(line => {
      try {
        // Strip SSE "data: " prefix if present
        const jsonLine = line.startsWith('data: ') ? line.slice(6) : line;
        return JSON.parse(jsonLine);
      } catch (e) {
        console.warn('[AgentEval] Failed to parse NDJSON line:', line);
        return null;
      }
    })
    .filter(Boolean);

  const steps: AgentEvalStep[] = [];
  let finalOutput = '';
  let totalCost = 0;
  let totalTokens = 0;
  const sessionId = `session-${startTime}`;

  for (const event of events) {
    const eventType = event.type;

    // Capture tool calls as steps
    if (eventType === 'tool_call') {
      steps.push({
        id: `step-${steps.length}`,
        name: event.tool || 'unknown',
        tool: event.tool || 'unknown',
        parameters: event.params || {},
        output: event.result,
        success: true,
        latency: 0,
        cost: 0,
      });
    }

    // Capture final message
    if (eventType === 'message_complete') {
      finalOutput = event.final?.text || '';
      totalCost = event.data?.metadata?.cost || 0;
      
      // Add synthesis step if present
      if (event.tool) {
        steps.push({
          id: `step-${steps.length}`,
          name: event.tool,
          tool: event.tool,
          parameters: {},
          success: event.ok || false,
          latency: 0,
          cost: totalCost,
        });
      }
    }

    // Accumulate streaming text (fallback if final not set)
    if (eventType === 'text_delta' && !finalOutput) {
      finalOutput += event.delta || '';
    }
  }

  const endTime = Date.now();
  const latency = endTime - startTime;

  return {
    session_id: sessionId,
    output: finalOutput,
    steps,
    cost: totalCost,
    latency,
    tokens: totalTokens,
  };
}

/**
 * Create AgentEval middleware handler
 *
 * @param config - Middleware configuration
 * @returns Request handler function
 */
export function createAgentEvalMiddleware(config: MiddlewareConfig) {
  const {
    targetEndpoint,
    transformRequest = defaultTransformRequest,
    parseResponse = defaultParseResponse,
    baseUrl,
    defaultUserId = 'agenteval-test-user',
    getUserId,
  } = config;

  return async function agentEvalHandler(req: any) {
    const startTime = Date.now();

    try {
      // Parse AgentEval request (Next.js App Router)
      const agentEvalReq: AgentEvalRequest = await req.json();

      // Resolve user ID (priority: context.userId > getUserId() > defaultUserId)
      if (!agentEvalReq.context) {
        agentEvalReq.context = {};
      }
      if (!agentEvalReq.context.userId) {
        agentEvalReq.context.userId = getUserId
          ? await getUserId(agentEvalReq)
          : defaultUserId;
      }

      console.log('[AgentEval] Received request:', {
        query: agentEvalReq.query,
        route: agentEvalReq.context?.route,
      });

      // Transform to target API format
      const targetReq = transformRequest(agentEvalReq);
      console.log('[AgentEval] Calling target endpoint:', targetEndpoint);

      // Determine base URL
      const host = req.headers?.get?.('host') || req.headers?.host || 'localhost:3000';
      const requestBaseUrl = baseUrl || `http://${host}`;

      // Call target endpoint
      const response = await fetch(`${requestBaseUrl}${targetEndpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(targetReq),
      });

      if (!response.ok) {
        throw new Error(`Target endpoint failed: ${response.status} ${response.statusText}`);
      }

      // Get response text
      const responseText = await response.text();
      console.log('[AgentEval] Received response, parsing...');

      // Parse and translate response
      const agentEvalRes = parseResponse(responseText, startTime);
      console.log('[AgentEval] Translated response:', {
        steps: agentEvalRes.steps.length,
        outputLength: agentEvalRes.output.length,
        cost: agentEvalRes.cost,
        latency: agentEvalRes.latency,
      });

      // Return JSON response (Next.js App Router format)
      return new Response(JSON.stringify(agentEvalRes), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    } catch (error: any) {
      console.error('[AgentEval] Error:', error);
      return new Response(
        JSON.stringify({
          error: error.message || 'AgentEval middleware failed',
          session_id: `error-${startTime}`,
          output: '',
          steps: [],
          cost: 0,
          latency: Date.now() - startTime,
        }),
        {
          status: 500,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }
  };
}
