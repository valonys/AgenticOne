export interface Citation {
  title: string;
  href: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  agentId?: AgentRole;
}

export interface UploadedFile {
  name: string;
  mimeType: string;
  data: string; // base64 encoded string
}

export interface UploadedFileState {
  file: UploadedFile;
  status: 'uploading' | 'processing' | 'ready';
  progress: number;
}

export type AgentRole = 'METHODS_SPECIALIST' | 'CORROSION_ENGINEER' | 'SUBSEA_ENGINEER' | 'DISCIPLINE_HEAD';

export interface Agent {
  id: AgentRole;
  name: string;
  description: string;
  systemPrompt: string;
  getWelcomeMessage: (userName: string) => string;
  avatar: string;
}

export interface RagSources {
  standards: boolean;
  internal: boolean;
  sensors: boolean;
  workorders: boolean;
}
