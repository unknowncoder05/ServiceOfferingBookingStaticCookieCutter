import React, { useState, useEffect } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { Agent, AgentAPI, Channel, mapAgentFromAPI } from '../../types/projectmaker';
import { api } from '../../services/api';

interface ProjectSidebarProps {
  isOpen: boolean;
}

export const ProjectSidebar: React.FC<ProjectSidebarProps> = ({ isOpen }) => {
  const location = useLocation();
  const { projectId } = useParams<{ projectId: string }>();
  const [currentProject, setCurrentProject] = useState<any>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);

  useEffect(() => {
    if (projectId) {
      loadSidebarData();
    }
  }, [projectId]);

  const loadSidebarData = async () => {
    try {
      // Load project details
      const projectResponse = await api.get(`/projects/${projectId}/`);
      setCurrentProject(projectResponse.data);

      // Load all agents from backend
      const agentsResponse = await api.get('/agents/');
      const agentData: AgentAPI[] = agentsResponse.data.results || agentsResponse.data;

      // Map all agents (built-in and custom) from API
      const allAgents = agentData.map((apiAgent) => mapAgentFromAPI(apiAgent, 0));

      // Sort: built-in agents first, then custom agents
      allAgents.sort((a, b) => {
        if (a.isCustom === b.isCustom) {
          return a.name.localeCompare(b.name);
        }
        return a.isCustom ? 1 : -1;
      });

      setAgents(allAgents);

      // Load channels
      const channelsResponse = await api.get(`/channels/?project=${projectId}`);
      const channelData = channelsResponse.data.results || channelsResponse.data;
      setChannels(channelData);
    } catch (error) {
      console.error('Error loading sidebar data:', error);
      // Fallback on error
      setCurrentProject({
        id: projectId,
        name: 'Project',
        phase: 'Unknown',
        progress: 0
      });
      setAgents([]);
      setChannels([]);
    }
  };

  const project = currentProject || {
    id: projectId || '1',
    name: 'Loading...',
    phase: 'Unknown',
    progress: 0
  };

  const dataSection = [
    { id: 'overview', name: 'Overview', icon: '📋' },
    { id: 'idea', name: 'Idea & Validation', icon: '💡' },
    { id: 'market', name: 'Market Research', icon: '📊' },
    { id: 'strategy', name: 'Strategy', icon: '🎯' },
    { id: 'financials', name: 'Financials', icon: '💰' },
    { id: 'legal', name: 'Legal & Compliance', icon: '⚖️' },
    { id: 'product', name: 'Product', icon: '🛠️' },
    { id: 'operations', name: 'Operations', icon: '🏭' },
    { id: 'team', name: 'Team', icon: '👥' },
    { id: 'marketing', name: 'Marketing', icon: '📣' },
    { id: 'sales', name: 'Sales', icon: '💼' },
    { id: 'metrics', name: 'Metrics & KPIs', icon: '📈' },
    { id: 'stakeholders', name: 'Stakeholders', icon: '🤝' },
    { id: 'risks', name: 'Risks', icon: '⚠️' },
  ];

  if (!isOpen) {
    return null;
  }

  return (
    <div className="w-64 bg-purple-900 text-white flex flex-col h-full overflow-hidden">
      {/* Project Selector */}
      <div className="p-4 border-b border-purple-800">
        <button className="w-full bg-purple-800 hover:bg-purple-700 rounded-lg p-3 text-left transition-colors">
          <div className="flex items-center justify-between">
            <span className="font-semibold truncate">{project.name}</span>
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
          <div className="mt-2 text-xs text-purple-300">{project.phase}</div>
          <div className="mt-2">
            <div className="h-1 bg-purple-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-400"
                style={{ width: `${project.progress}%` }}
              ></div>
            </div>
            <div className="text-xs text-purple-300 mt-1">{project.progress}% Complete</div>
          </div>
        </button>
      </div>

      {/* Quick Access */}
      <div className="px-3 py-3 border-b border-purple-800">
        <Link
          to={`/projects/${project.id}/dashboard`}
          className={`flex items-center gap-2 px-3 py-2 rounded transition-colors text-sm ${
            location.pathname.endsWith('/dashboard') ? 'bg-purple-700 text-white' : 'hover:bg-purple-800'
          }`}
        >
          <span>📊</span>
          <span>Project Dashboard</span>
        </Link>
        <Link
          to={`/projects/${project.id}/resources`}
          className={`flex items-center gap-2 px-3 py-2 rounded transition-colors text-sm ${
            location.pathname.includes('/resources') ? 'bg-purple-700 text-white' : 'hover:bg-purple-800'
          }`}
        >
          <span>📁</span>
          <span>Resources</span>
        </Link>
        <Link
          to={`/projects/${project.id}/backlog`}
          className={`flex items-center gap-2 px-3 py-2 rounded transition-colors text-sm ${
            location.pathname.includes('/backlog') ? 'bg-purple-700 text-white' : 'hover:bg-purple-800'
          }`}
        >
          <span>📝</span>
          <span>Backlog</span>
        </Link>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 overflow-y-auto">
        {/* Agents Section */}
        <div className="px-3 py-3 border-b border-purple-800">
          <div className="text-xs font-semibold text-purple-300 mb-2 px-3">AGENTS</div>
          <div className="space-y-0.5">
            {agents.map((agent) => {
              const isActive = location.pathname.includes(`/agents/${agent.id}`);
              return (
                <Link
                  key={agent.id}
                  to={`/projects/${project.id}/agents/${agent.id}`}
                  className={`flex items-center justify-between px-3 py-2 rounded transition-colors ${
                    isActive ? 'bg-purple-700 text-white' : 'text-purple-100 hover:bg-purple-800'
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-lg flex-shrink-0">{agent.avatar}</span>
                    <span className="text-sm truncate">{agent.name}</span>
                  </div>
                  {agent.unreadCount > 0 && (
                    <span className="bg-red-500 text-white text-xs rounded-full px-2 py-0.5 flex-shrink-0">
                      {agent.unreadCount}
                    </span>
                  )}
                </Link>
              );
            })}
            <button className="w-full text-left px-3 py-2 text-sm text-purple-300 hover:text-white hover:bg-purple-800 rounded transition-colors">
              + Add Custom Agent
            </button>
          </div>
        </div>

        {/* Channels Section */}
        <div className="px-3 py-3 border-b border-purple-800">
          <div className="text-xs font-semibold text-purple-300 mb-2 px-3">CHANNELS</div>
          <div className="space-y-0.5">
            {channels.map((channel) => {
              const isActive = location.pathname.includes(`/channels/${channel.id}`);
              return (
                <Link
                  key={channel.id}
                  to={`/projects/${project.id}/channels/${channel.id}`}
                  className={`flex items-center justify-between px-3 py-2 rounded transition-colors ${
                    isActive ? 'bg-purple-700 text-white' : 'text-purple-100 hover:bg-purple-800'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-purple-400">#</span>
                    <span className="text-sm">{channel.name}</span>
                  </div>
                  {channel.unreadCount > 0 && (
                    <span className="bg-red-500 text-white text-xs rounded-full px-2 py-0.5">
                      {channel.unreadCount}
                    </span>
                  )}
                </Link>
              );
            })}
            <button className="w-full text-left px-3 py-2 text-sm text-purple-300 hover:text-white hover:bg-purple-800 rounded transition-colors">
              + Create Channel
            </button>
          </div>
        </div>

        {/* Project Data Section */}
        <div className="px-3 py-3">
          <div className="text-xs font-semibold text-purple-300 mb-2 px-3">PROJECT DATA</div>
          <div className="space-y-0.5">
            {dataSection.map((section) => {
              const isActive = location.pathname.includes(`/data/${section.id}`);
              return (
                <Link
                  key={section.id}
                  to={`/projects/${project.id}/data/${section.id}`}
                  className={`flex items-center gap-2 px-3 py-2 rounded transition-colors text-sm ${
                    isActive ? 'bg-purple-700 text-white' : 'text-purple-100 hover:bg-purple-800'
                  }`}
                >
                  <span>{section.icon}</span>
                  <span className="truncate">{section.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
