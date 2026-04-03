import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  type Tool,
} from "@modelcontextprotocol/sdk/types.js";
import axios, { type AxiosRequestConfig } from "axios";
import dotenv from "dotenv";

dotenv.config();

const API_URL = process.env.BOOSTCAMP_API_URL || "http://localhost:5000/api/v1";
const AUTH_TOKEN = process.env.BOOSTCAMP_AUTH_TOKEN || "";

const config: AxiosRequestConfig = {
  baseURL: API_URL,
};

if (AUTH_TOKEN) {
  config.headers = {
    Authorization: `Bearer ${AUTH_TOKEN}`,
  };
}

const apiClient = axios.create(config);

const server = new Server(
  {
    name: "boostcamp-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const TOOLS: Tool[] = [
  {
    name: "get_bootcamps",
    description: "Get all bootcamps with filtering and pagination",
    inputSchema: {
      type: "object",
      properties: {
        page: { type: "number", description: "Page number" },
        limit: { type: "number", description: "Limit per page" },
        select: { type: "string", description: "Fields to select" },
        sort: { type: "string", description: "Fields to sort by" },
      },
    },
  },
  {
    name: "get_bootcamp",
    description: "Get a single bootcamp by ID",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Bootcamp ID" },
      },
      required: ["id"],
    },
  },
  {
    name: "get_courses",
    description: "Get all courses",
    inputSchema: {
      type: "object",
      properties: {
        bootcampId: { type: "string", description: "Optional bootcamp ID to filter by" },
      },
    },
  },
  {
    name: "get_reviews",
    description: "Get all reviews",
    inputSchema: {
      type: "object",
      properties: {
        bootcampId: { type: "string", description: "Optional bootcamp ID to filter by" },
      },
    },
  },
  {
    name: "get_bootcamps_radius",
    description: "Get bootcamps within a radius of a zipcode",
    inputSchema: {
      type: "object",
      properties: {
        zipcode: { type: "string", description: "Zipcode" },
        distance: { type: "number", description: "Distance in miles" },
      },
      required: ["zipcode", "distance"],
    },
  },
  {
    name: "create_bootcamp",
    description: "Create a new bootcamp (Requires Publisher/Admin roles)",
    inputSchema: {
      type: "object",
      properties: {
        name: { type: "string" },
        description: { type: "string" },
        website: { type: "string" },
        phone: { type: "string" },
        email: { type: "string" },
        address: { type: "string" },
        careers: { type: "array", items: { type: "string" } },
        housing: { type: "boolean" },
        jobAssistance: { type: "boolean" },
        jobGuarantee: { type: "boolean" },
        acceptGi: { type: "boolean" },
      },
      required: ["name", "description", "website", "phone", "email", "address", "careers"],
    },
  },
];

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "get_bootcamps": {
        const response = await apiClient.get("/bootcamps", { params: args });
        return {
          content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
        };
      }
      case "get_bootcamp": {
        const { id } = args as { id: string };
        const response = await apiClient.get(`/bootcamps/${id}`);
        return {
          content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
        };
      }
      case "get_courses": {
        const { bootcampId } = args as { bootcampId?: string };
        const url = bootcampId ? `/bootcamps/${bootcampId}/courses` : "/courses";
        const response = await apiClient.get(url);
        return {
          content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
        };
      }
      case "get_reviews": {
        const { bootcampId } = args as { bootcampId?: string };
        const url = bootcampId ? `/bootcamps/${bootcampId}/reviews` : "/reviews";
        const response = await apiClient.get(url);
        return {
          content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
        };
      }
      case "get_bootcamps_radius": {
        const { zipcode, distance } = args as { zipcode: string; distance: number };
        const response = await apiClient.get(`/bootcamps/radius/${zipcode}/${distance}`);
        return {
          content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
        };
      }
      case "create_bootcamp": {
        const response = await apiClient.post("/bootcamps", args);
        return {
          content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
        };
      }
      default:
        throw new Error(`Tool not found: ${name}`);
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.response?.data?.error || error.message}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Boostcamp MCP server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
