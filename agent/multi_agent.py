"""
PersonalMind 多智能体团队

创建一个 AI Agent 团队，每个 Agent 有专长：
- 研究助手：搜索、分析、总结
- 生活管家：日常事务、日程、提醒
- 创意师：头脑风暴、创意生成
- 开发者：代码、技术问题
"""
import os
import time
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class AgentRole(Enum):
    """Agent 角色"""
    RESEARCHER = "researcher"    # 研究助手
    LIFE_COACH = "life_coach"  # 生活管家
    CREATIVITY = "creativity"   # 创意师
    CODER = "coder"            # 开发者


@dataclass
class Agent:
    """Agent 定义"""
    name: str
    role: AgentRole
    description: str
    system_prompt: str
    avatar: str  # Emoji 头像
    specialty: List[str] = field(default_factory=list)


@dataclass
class Message:
    """消息"""
    sender: str
    receiver: str  # 'all' 表示广播
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class MultiAgentTeam:
    """
    多智能体团队
    
    多个 Agent 协作解决问题
    """
    
    def __init__(self, llm_func: Callable):
        """
        Args:
            llm_func: LLM 调用函数
        """
        self.llm = llm_func
        self.agents: Dict[str, Agent] = {}
        self.messages: List[Message] = []
        self._init_agents()
    
    def _init_agents(self):
        """初始化团队成员"""
        # 研究助手
        self.register(Agent(
            name="研究员",
            role=AgentRole.RESEARCHER,
            description="擅长搜索信息、分析数据、总结报告",
            avatar="🔍",
            specialty=["信息检索", "数据分析", "报告撰写", "竞品分析"]
        ))
        
        # 生活管家
        self.register(Agent(
            name="管家",
            role=AgentRole.LIFE_COACH,
            description="擅长日程管理、生活建议、健康提醒",
            avatar="🏠",
            specialty=["日程安排", "健康建议", "生活技巧", "情绪陪伴"]
        ))
        
        # 创意师
        self.register(Agent(
            name="创意师",
            role=AgentRole.CREATIVITY,
            description="擅长头脑风暴、创意生成、问题解决",
            avatar="💡",
            specialty=["头脑风暴", "创意构思", "问题解决", "故事创作"]
        ))
        
        # 开发者
        self.register(Agent(
            name="开发者",
            role=AgentRole.CODER,
            description="擅长代码编写、技术问题、Bug 修复",
            avatar="💻",
            specialty=["代码开发", "架构设计", "Bug修复", "性能优化"]
        ))
    
    def register(self, agent: Agent):
        """注册 Agent"""
        self.agents[agent.name] = agent
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """获取 Agent"""
        return self.agents.get(name)
    
    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """根据角色获取 Agent"""
        return [a for a in self.agents.values() if a.role == role]
    
    def chat(self, user_input: str, team_mode: bool = True) -> str:
        """
        团队对话
        
        Args:
            user_input: 用户输入
            team_mode: 是否启用团队模式
        
        Returns:
            团队回复
        """
        if not team_mode:
            # 单 Agent 模式（默认使用研究员）
            return self._single_agent_response("研究员", user_input)
        
        # 团队协作模式
        return self._team_response(user_input)
    
    def _single_agent_response(self, agent_name: str, user_input: str) -> str:
        """单个 Agent 响应"""
        agent = self.get_agent(agent_name)
        if not agent:
            return "Agent 不存在"
        
        prompt = f"{agent.system_prompt}\n\n用户问题: {user_input}"
        return self.llm(prompt)
    
    def _team_response(self, user_input: str) -> str:
        """
        团队协作响应
        
        流程：
        1. 分析问题类型
        2. 确定参与的 Agent
        3. 并行收集各 Agent 意见
        4. 综合输出团队回复
        """
        # 1. 确定需要哪些 Agent
        needed_agents = self._determine_agents(user_input)
        
        if not needed_agents:
            # 没有匹配，随便选一个
            needed_agents = ["研究员"]
        
        # 2. 并行收集各 Agent 意见
        responses = {}
        for agent_name in needed_agents:
            agent = self.get_agent(agent_name)
            if agent:
                # 构建 Agent 专属提示
                prompt = self._build_agent_prompt(agent, user_input)
                # 这里简化处理，实际应该异步调用
                response = self._get_agent_response(agent, user_input)
                responses[agent_name] = response
        
        # 3. 综合输出
        return self._synthesize_response(user_input, responses)
    
    def _determine_agents(self, user_input: str) -> List[str]:
        """根据问题类型确定需要的 Agent"""
        needed = []
        
        keywords = {
            "研究员": ["搜索", "查找", "分析", "总结", "报告", "新闻", "最新", "研究", "论文"],
            "管家": ["日程", "安排", "提醒", "健康", "生活", "习惯", "减肥", "运动", "吃饭", "休息"],
            "创意师": ["创意", "头脑风暴", "想法", "建议", "怎么", "如何", "方案", "策划"],
            "开发者": ["代码", "编程", "Bug", "Python", "开发", "技术", "函数", "算法"]
        }
        
        for agent_name, trigger_words in keywords.items():
            if any(word in user_input for word in trigger_words):
                if agent_name not in needed:
                    needed.append(agent_name)
        
        return needed
    
    def _build_agent_prompt(self, agent: Agent, user_input: str) -> str:
        """构建 Agent 专属提示"""
        specialty_text = "、".join(agent.specialty)
        
        prompt = f"""你是 {agent.avatar} {agent.name}，{agent.description}
专长领域：{specialty_text}

用户问题：{user_input}

请基于你的专长，提供专业建议。回复简洁有条理，突出你的专业视角。"""
        
        return prompt
    
    def _get_agent_response(self, agent: Agent, user_input: str) -> Dict:
        """获取单个 Agent 的响应"""
        prompt = self._build_agent_prompt(agent, user_input)
        
        try:
            response = self.llm(prompt)
        except Exception as e:
            response = f"（{agent.name}暂时无法回复）"
        
        return {
            "agent": agent,
            "response": response,
            "timestamp": datetime.now()
        }
    
    def _synthesize_response(self, user_input: str, responses: Dict) -> str:
        """综合各 Agent 意见"""
        if len(responses) == 1:
            # 只有一个 Agent，直接返回
            return list(responses.values())[0]["response"]
        
        # 多个 Agent，综合输出
        header = f"🤖 **PersonalMind 团队响应**\n\n"
        header += f"问题：{user_input}\n\n"
        header += "---\n\n"
        
        parts = []
        for agent_name, data in responses.items():
            agent = data["agent"]
            response = data["response"]
            parts.append(f"{agent.avatar} **{agent.name}** 的看法：\n{response}\n")
        
        # 整体总结
        if len(responses) > 1:
            parts.append("💬 **总结**\n")
            parts.append("以上是团队各成员的专业意见，你可以综合考虑。")
        
        return header + "\n".join(parts)
    
    def broadcast(self, sender: str, message: str):
        """广播消息"""
        msg = Message(sender=sender, receiver="all", content=message)
        self.messages.append(msg)
    
    def private_message(self, sender: str, receiver: str, message: str):
        """发送私信"""
        msg = Message(sender=sender, receiver=receiver, content=message)
        self.messages.append(msg)
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return [
            {
                "from": m.sender,
                "to": m.receiver,
                "content": m.content,
                "time": m.timestamp.strftime("%H:%M")
            }
            for m in self.messages[-20:]  # 最近20条
        ]


def demo():
    """演示"""
    print("=" * 60)
    print("PersonalMind 多智能体团队演示")
    print("=" * 60)
    
    # 模拟 LLM
    def mock_llm(prompt: str) -> str:
        return f"【基于提示词的回复】\n这是对问题的回答：{prompt[:50]}..."
    
    # 创建团队
    team = MultiAgentTeam(mock_llm)
    
    print(f"\n团队成员：")
    for name, agent in team.agents.items():
        print(f"  {agent.avatar} {name} - {agent.description}")
    
    # 测试问题
    questions = [
        ("帮我搜索一下今天有什么科技新闻", True),
        ("我最近想减肥，有什么建议吗？", True),
        ("如何提高代码质量？", True),
        ("帮我策划一个产品发布会", True),
    ]
    
    print("\n" + "=" * 60)
    print("团队协作演示")
    print("=" * 60)
    
    for question, team_mode in questions:
        print(f"\n👤 用户：{question}")
        print("-" * 40)
        
        # 确定参与的 Agent
        needed = team._determine_agents(question)
        print(f"🔍 确定的 Agent：{', '.join(needed) if needed else '研究员'}")
        
        # 获取响应
        response = team.chat(question, team_mode=team_mode)
        print(f"\n🤖 团队回复：\n{response[:200]}...")
        print()


if __name__ == "__main__":
    demo()
