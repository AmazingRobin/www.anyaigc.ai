"""Localized editorial copy derived from the AnyAIGC Doubao model catalog.

Source: https://anyaigc.ai/pricing?provider=Doubao, captured in
.playwright-mcp/doubao-research.json. Full snapshot IDs are dictionary keys
only; visible copy uses date-free names. No prices or throughput promises
are included here. Use cases are suggested applications of listed abilities.
"""

COPY = {
    "doubao-seed-2-1-pro-260915": {
        "zh": {
            "tagline": "子任务协同执行",
            "summary": "面向需要持续推进的复杂 Agent 任务，结合多模态理解与异步子任务协同。模型可协调并验收子任务，将图片、视频和页面中的信息用于推理判断与操作，适用于深度调研和办公协作。",
            "features": [
                ("异步子任务协同", "围绕主任务协调异步子任务，并检查子任务的交付结果，帮助衔接多阶段工作。"),
                ("视觉信息参与执行", "理解图片、视频和页面内容，将视觉线索纳入推理判断与实际操作。"),
                ("持续推进复杂任务", "面向长程任务保持执行进展，支持调研、资料整理与协作过程中的连续工作。"),
            ],
            "uses": [
                ("调研", "多来源研究协作", "把研究问题拆成可协作的子任务，核对各项发现，再整理成有依据的研究结论。"),
                ("办公", "跨材料任务交付", "结合页面、图片和文档中的信息，安排资料整理与核验步骤，形成办公交付物。"),
                ("Agent", "子任务验收", "为各个子任务定义完成条件，检查返回结果，识别仍需补充的工作。"),
            ],
            "prompt": "为一项竞品调研设计三个可并行的子任务，分别给出输入材料、交付物和验收标准。",
        },
        "en": {
            "tagline": "Coordinated agent execution",
            "summary": "Built for complex agent work that spans multiple stages. It coordinates and reviews asynchronous subtasks, using images, video, and page content to inform reasoning and actions in research and office workflows.",
            "features": [
                ("Asynchronous coordination", "Coordinate subtasks around a shared objective and review their deliverables before moving the broader task forward."),
                ("Visual context for actions", "Use information from images, video, and pages to inform reasoning, decisions, and execution."),
                ("Long-running task progress", "Carry complex work across successive stages of research, organization, and collaboration."),
            ],
            "uses": [
                ("Research", "Coordinate a research brief", "Split a research question into subtasks, check the findings, and assemble an evidence-based brief."),
                ("Office", "Work across mixed materials", "Plan the collection and review of information from pages, images, and documents for a shared deliverable."),
                ("Agents", "Review subtask results", "Define completion criteria, assess returned work, and identify what still needs attention."),
            ],
            "prompt": "Design three parallel subtasks for a competitive research project. Specify the inputs, deliverables, and acceptance criteria for each.",
        },
    },
    "doubao-seed-2-1-turbo-260628": {
        "zh": {
            "tagline": "规模化研发任务",
            "summary": "面向规模化生产场景的 Seed 2.1 版本，聚焦 Coding 工程交付、Agent 长链路执行和多模态理解。通过自主规划与动态修复能力，承接真实研发流程中的任务推进和问题处理。",
            "features": [
                ("工程交付导向", "围绕研发任务组织代码工作，将需求、实现步骤和交付检查连接起来。"),
                ("长链路 Agent", "支持跨多个阶段推进任务，在执行中结合新信息调整后续计划。"),
                ("动态修复与理解", "结合多模态理解识别任务中的问题，并协助修正代码或执行方案。"),
            ],
            "uses": [
                ("研发", "日常工程任务", "把常见功能需求转成实现计划，协助编码与检查，适配持续开展的研发工作。"),
                ("自动化", "多步骤业务流程", "为包含多个处理阶段的任务安排执行顺序，并在遇到问题时调整方案。"),
                ("维护", "错误反馈与修复", "依据错误信息和现有实现定位问题，提出修复方案与验证步骤。"),
            ],
            "prompt": "为一个 CSV 导入功能制定实现计划，包含字段校验、重复记录处理、错误提示和验证步骤。",
        },
        "en": {
            "tagline": "Coding at production scale",
            "summary": "The Seed 2.1 variant aimed at scaled production workloads. It combines coding delivery, extended agent execution, and multimodal understanding with autonomous planning and dynamic repair for ongoing engineering work.",
            "features": [
                ("Engineering delivery", "Connect requirements, implementation steps, and delivery checks within a coding task."),
                ("Extended agent workflows", "Advance work through multiple stages and revise the plan as new information becomes available."),
                ("Dynamic repair", "Use task feedback and multimodal context to help identify problems and revise code or execution plans."),
            ],
            "uses": [
                ("Engineering", "Recurring development work", "Turn routine feature requests into implementation plans with coding assistance and review steps."),
                ("Automation", "Multi-stage processes", "Organize a sequence of business tasks and revise the approach when an intermediate step needs attention."),
                ("Maintenance", "Feedback-driven fixes", "Analyze an error alongside the implementation, then propose a fix and a way to validate it."),
            ],
            "prompt": "Plan a CSV import feature with field validation, duplicate handling, error messages, and verification steps.",
        },
    },
    "doubao-seed-2-1-pro-260628": {
        "zh": {
            "tagline": "规划执行与修复",
            "summary": "面向企业复杂任务的 Seed 2.1 Pro，结合 Coding、Agent 与多模态能力。重点在自主规划、长链路执行和动态修复，让研发需求和业务目标能够分步推进，并根据执行反馈调整方案。",
            "features": [
                ("自主规划", "从复杂目标中梳理约束与依赖，形成可逐步执行的工作安排。"),
                ("长链路执行", "围绕目标衔接多个工作阶段，处理真实任务中相互依赖的步骤。"),
                ("执行中的动态修复", "结合代码、任务反馈与多模态信息调整方案，协助处理推进过程中的问题。"),
            ],
            "uses": [
                ("工程", "复杂功能开发", "拆解涉及多个模块的开发需求，明确依赖顺序、实现方案和验证事项。"),
                ("Agent", "多阶段任务规划", "为跨步骤的企业任务建立执行计划，并根据阶段结果修订后续安排。"),
                ("排障", "迭代修复方案", "结合当前实现与反馈分析失败原因，提出下一轮修改和检查步骤。"),
            ],
            "prompt": "把一个订单退款功能拆成实施步骤，说明状态流转、接口依赖、异常处理和验收要点。",
        },
        "en": {
            "tagline": "Plan, execute, and repair",
            "summary": "Seed 2.1 Pro brings coding, agent execution, and multimodal understanding to complex enterprise tasks. Its focus is autonomous planning, work across multiple stages, and dynamic repair as execution feedback arrives.",
            "features": [
                ("Autonomous planning", "Identify constraints and dependencies within a complex objective and organize the work into actionable stages."),
                ("Long-horizon execution", "Connect interdependent steps across a task while keeping the broader objective in view."),
                ("Repair during execution", "Use code, feedback, and multimodal information to revise the approach when problems arise."),
            ],
            "uses": [
                ("Engineering", "Complex feature delivery", "Break a feature spanning several modules into dependencies, implementation steps, and verification tasks."),
                ("Agents", "Plan multi-stage work", "Build an execution plan for a business objective and update later steps using intermediate results."),
                ("Debugging", "Iterative repair plans", "Analyze a failure against the current implementation and propose the next changes and checks."),
            ],
            "prompt": "Break an order refund feature into implementation steps. Cover state transitions, API dependencies, failure handling, and acceptance criteria.",
        },
    },
    "doubao-seed-2-0-pro-260215": {
        "zh": {
            "tagline": "复杂推理与规划",
            "summary": "面向 Agent 场景的通用模型，兼顾复杂推理、长上下文理解与工具增强执行。它适合处理多重约束和多步骤规划，也能结合图像、视频等内容分析问题，生成结构化的任务结果。",
            "features": [
                ("多约束推理", "在复杂指令和多项约束下分析问题，梳理条件、依赖及可行的处理步骤。"),
                ("视觉与视频理解", "结合图像、视频和文本信息进行分析，支持跨模态的推理任务。"),
                ("工具增强执行", "将多步骤规划与工具使用相结合，并以结构化内容组织任务结果。"),
            ],
            "uses": [
                ("分析", "多条件方案比较", "根据预算、资源和时间等条件比较候选方案，说明各自的依据与限制。"),
                ("内容", "视频内容分析", "围绕视频中的事件与画面信息组织分析，整理关键内容和后续问题。"),
                ("Agent", "工具辅助任务", "规划需要外部工具参与的处理步骤，汇总工具结果并形成结构化结论。"),
            ],
            "prompt": "为一个两周上线的内部知识库项目比较三种实施方案，按人力、维护成本和交付风险列出取舍。",
        },
        "en": {
            "tagline": "Reasoning under constraints",
            "summary": "A general-purpose model for agent workflows that combine complex reasoning, long-context analysis, and tool-assisted execution. It handles multi-step planning and multimodal material, with structured generation for organizing results.",
            "features": [
                ("Multi-constraint reasoning", "Analyze complex instructions, trace dependencies, and work through several requirements within the same task."),
                ("Images and video", "Bring visual and video information into analysis alongside text."),
                ("Tool-assisted execution", "Combine planning with tool use and organize the resulting findings into structured content."),
            ],
            "uses": [
                ("Analysis", "Compare constrained options", "Evaluate candidate plans against budget, staffing, and time constraints, explaining the tradeoffs."),
                ("Media", "Analyze video content", "Organize observations about events and visual details into a focused content analysis."),
                ("Agents", "Tool-assisted workflows", "Plan external tool steps, consolidate their results, and prepare a structured conclusion."),
            ],
            "prompt": "Compare three ways to launch an internal knowledge base in two weeks. Explain staffing needs, maintenance costs, and delivery risks.",
        },
    },
    "doubao-seed-2-0-lite-260215": {
        "zh": {
            "tagline": "高频信息处理",
            "summary": "面向高频企业任务，覆盖非结构化信息处理、内容创作、搜索推荐和数据分析。它支持长上下文、多来源信息融合及多步骤指令执行，适合把分散材料整理成可供业务系统使用的结构化内容。",
            "features": [
                ("非结构化信息整理", "从长文和分散材料中提取关键事实，组织成便于后续处理的内容。"),
                ("多来源信息融合", "结合长上下文处理多份材料，汇总相同主题下的信息与差异。"),
                ("结构化内容生成", "按照指定字段和格式组织输出，适合需要连续处理多步骤指令的业务任务。"),
            ],
            "uses": [
                ("运营", "内容批量整理", "把活动资料、产品说明和用户反馈整理成统一格式的摘要或内容草稿。"),
                ("数据", "业务字段提取", "从非结构化文本中提取所需字段，并标记材料未提供的信息。"),
                ("搜索", "搜索结果归纳", "合并多条搜索结果的主要观点，梳理共同信息与仍需核验的差异。"),
            ],
            "prompt": "从这段反馈提取产品、问题和用户诉求，以 JSON 返回：用户购买了便携灯，充电后只能使用一小时，希望更换。",
        },
        "en": {
            "tagline": "Everyday enterprise processing",
            "summary": "Designed for frequent enterprise tasks such as unstructured information processing, content creation, search, and data analysis. Long-context understanding and multi-source synthesis help turn scattered material into structured business content.",
            "features": [
                ("Unstructured information", "Extract key facts from long passages and scattered source material for downstream processing."),
                ("Multi-source synthesis", "Bring several documents into one context and organize their common points and differences."),
                ("Structured generation", "Follow multi-step instructions and arrange results around the fields and format a workflow requires."),
            ],
            "uses": [
                ("Operations", "Organize recurring content", "Convert campaign notes, product descriptions, and feedback into consistently formatted briefs or drafts."),
                ("Data", "Extract business fields", "Pull required fields from free-form text and identify information that the source does not supply."),
                ("Search", "Synthesize search results", "Combine the main points across results and identify disagreements that need further checking."),
            ],
            "prompt": "Extract the product, issue, and customer request as JSON: A customer bought a portable lamp. It lasts only one hour after charging, and they want a replacement.",
        },
    },
    "doubao-seed-2-0-lite-260428": {
        "zh": {
            "tagline": "原生全模态理解",
            "summary": "以原生统一理解连接视频、图片、音频和文本，同时增强 Agent、Coding 与 GUI 能力。适合需要结合多类输入理解任务，并将信息分析衔接到编程或界面操作规划的应用。",
            "features": [
                ("统一理解多类输入", "结合视频、图片、音频和文本中的信息，在同一任务中理解不同形式的材料。"),
                ("Agent 与编程", "在多模态理解基础上处理 Agent 任务与 Coding 工作，连接信息分析和实现需求。"),
                ("GUI 理解与操作", "围绕图形界面理解页面状态与操作目标，辅助组织界面交互步骤。"),
            ],
            "uses": [
                ("音视频", "混合材料整理", "结合音频、视频及文字资料理解同一主题，梳理主要信息和待办事项。"),
                ("界面", "操作步骤规划", "根据界面内容和目标任务，说明接下来需要完成的交互步骤。"),
                ("研发", "多模态需求理解", "结合界面资料和文字需求整理开发任务，帮助衔接需求分析与代码实现。"),
            ],
            "prompt": "为一个文件上传界面设计交互流程，覆盖拖放、上传进度、失败重试和完成反馈。",
        },
        "en": {
            "tagline": "Native omnimodal understanding",
            "summary": "Unifies understanding of video, images, audio, and text, alongside enhanced agent, coding, and GUI capabilities. It suits applications that need to interpret mixed inputs and connect that information to programming or interface tasks.",
            "features": [
                ("Unified input understanding", "Interpret video, images, audio, and text together within a task."),
                ("Agents and coding", "Connect multimodal analysis with agent workflows and programming requirements."),
                ("GUI capabilities", "Interpret interface states and task goals to help organize interactions with graphical interfaces."),
            ],
            "uses": [
                ("Media", "Organize mixed materials", "Combine audio, video, and written notes about a topic to identify key information and follow-up work."),
                ("Interfaces", "Plan interface interactions", "Use the current interface and intended outcome to outline the next interaction steps."),
                ("Engineering", "Interpret visual requirements", "Combine interface references and written requirements into development tasks."),
            ],
            "prompt": "Design the interaction flow for a file upload interface, including drag and drop, upload progress, retries, and completion feedback.",
        },
    },
    "doubao-seed-1-8-251228": {
        "zh": {
            "tagline": "多模态业务助手",
            "summary": "围绕多模态理解与 Agent 能力构建企业应用，适合将图文信息理解接入实际业务任务。可用于材料分析、任务安排和工具协作，让企业助手既能理解输入内容，也能参与后续工作流程。",
            "features": [
                ("多模态理解", "理解文字与图像等输入内容，将不同来源的信息用于任务分析。"),
                ("Agent 能力", "面向需要执行多个步骤的实际工作，帮助组织任务并参与工作流程。"),
                ("业务工具协作", "模型目录列有工具能力，可用于衔接业务助手与应用侧提供的工具。"),
            ],
            "uses": [
                ("业务", "图文材料分析", "结合说明文字和图片理解业务材料，整理重点与需要补充的信息。"),
                ("助手", "企业任务安排", "把员工提出的业务目标整理为明确步骤，帮助衔接后续处理。"),
                ("工具", "工作流程衔接", "将理解与任务安排接入企业应用，由应用侧工具完成对应业务操作。"),
            ],
            "prompt": "把新员工入职准备整理成任务清单，分别列出人事、IT 和直属经理需要完成的事项。",
        },
        "en": {
            "tagline": "Multimodal business assistance",
            "summary": "Combines multimodal understanding with agent capabilities for practical enterprise work. It can help analyze visual and written materials, organize tasks, and connect an assistant to application-provided tools.",
            "features": [
                ("Multimodal understanding", "Use text, images, and other supported inputs to understand the materials behind a business task."),
                ("Agent capabilities", "Help organize the steps involved in practical work and participate in broader workflows."),
                ("Business tool integration", "The catalog lists tool capabilities for connecting an assistant to tools supplied by the application."),
            ],
            "uses": [
                ("Business", "Analyze visual materials", "Read images alongside written descriptions to identify key information and missing context."),
                ("Assistants", "Organize workplace tasks", "Turn an employee's objective into clear steps that can be handed off for execution."),
                ("Tools", "Connect business workflows", "Bring understanding and task planning into an application whose tools carry out the required operations."),
            ],
            "prompt": "Create an onboarding preparation checklist with separate responsibilities for HR, IT, and the new employee's manager.",
        },
    },
    "doubao-seed-2-0-mini-260428": {
        "zh": {
            "tagline": "高效全模态理解",
            "summary": "强调更短思考长度和 token 使用效率的全模态理解模型。适合在多类输入理解中控制思考开销，为内容初筛、简要问答和日常信息整理提供轻量选择，并让输出聚焦任务需要的关键信息。",
            "features": [
                ("全模态理解", "围绕不同形式的输入理解任务内容，适用于需要综合处理多类信息的应用。"),
                ("较短思考长度", "模型定位强调缩短思考过程，面向不需要展开长篇推理的处理任务。"),
                ("Token 使用效率", "关注完成任务时的 token 效率，便于评估日常处理流程的资源开销。"),
            ],
            "uses": [
                ("初筛", "内容快速归类", "为进入工作流的材料提供初步分类与简要说明，再交给后续环节处理。"),
                ("问答", "聚焦关键答案", "围绕给定材料回答具体问题，按要求限制篇幅，减少不必要的展开。"),
                ("整理", "简明材料摘要", "将多类材料中的主要信息整理成少量要点，方便人员快速浏览。"),
            ],
            "prompt": "用三个要点概括这份通知：本周五 18 点进行系统维护，预计持续两小时，期间报表导出暂停，其他功能正常。",
        },
        "en": {
            "tagline": "Token-efficient omnimodal tasks",
            "summary": "An omnimodal understanding model focused on shorter reasoning and higher token efficiency. Consider it for initial content triage, focused questions, and concise summaries where the task calls for a compact result.",
            "features": [
                ("Omnimodal understanding", "Interpret different forms of input in applications that need to work across multiple types of information."),
                ("Shorter reasoning", "Its design emphasizes a shorter thinking process for tasks that do not require extended analysis."),
                ("Token efficiency", "Focuses on efficient token use when handling recurring processing work."),
            ],
            "uses": [
                ("Triage", "Initial content routing", "Assign incoming material a preliminary category and brief explanation for the next workflow stage."),
                ("Questions", "Focused answers", "Answer a specific question about supplied material with a concise response."),
                ("Summaries", "Compact information briefs", "Reduce the main information in mixed materials to a small set of points for quick review."),
            ],
            "prompt": "Summarize this notice in three bullets: System maintenance starts Friday at 6 p.m. and lasts about two hours. Report exports will be unavailable; other features will remain available.",
        },
    },
    "doubao-seed-2-0-code-preview-260215": {
        "zh": {
            "tagline": "企业编程与前端",
            "summary": "面向企业编程需求，在 Seed 2.0 的 Agent 与视觉语言能力基础上强化代码生成。重点覆盖前端开发以及企业常见的多语言编程场景，适合接入 AI 编程工具，辅助从需求理解到代码实现的过程。",
            "features": [
                ("前端开发", "围绕界面结构、交互需求与实现细节生成代码，服务前端工程任务。"),
                ("多语言编程", "针对企业环境中的多种编程语言场景优化代码生成与开发辅助能力。"),
                ("Agent 与视觉语言基础", "结合任务执行和视觉语言理解能力，帮助理解开发材料并推进编程工作。"),
            ],
            "uses": [
                ("前端", "交互组件实现", "把页面与交互需求转成组件实现，补充状态处理和边界情况。"),
                ("工程", "跨语言开发辅助", "在不同语言的业务模块中生成代码草稿、解释实现并整理修改建议。"),
                ("工具", "AI 编程工作台", "把模型接入编程工具，为需求拆解、代码生成和迭代修改提供支持。"),
            ],
            "prompt": "用原生 HTML、CSS 和 JavaScript 编写一个可键盘操作的标签页组件，包含三个面板，并解释状态切换逻辑。",
        },
        "en": {
            "tagline": "Enterprise coding and frontend",
            "summary": "Optimized for enterprise programming, with stronger code generation built on Seed 2.0's agent and vision-language capabilities. Its focus includes frontend development and multilingual coding workflows, making it a candidate for AI programming tools.",
            "features": [
                ("Frontend development", "Generate code around interface structure, interaction requirements, and implementation details."),
                ("Multilingual coding", "Support code generation and development tasks across programming languages used in enterprise environments."),
                ("Agent and visual foundations", "Combine task execution with vision-language understanding to interpret development materials and advance coding work."),
            ],
            "uses": [
                ("Frontend", "Build interactive components", "Translate interface requirements into component code with state handling and edge cases."),
                ("Engineering", "Work across languages", "Draft code, explain implementations, and propose changes in business modules written in different languages."),
                ("Tools", "AI programming workspaces", "Integrate the model into a coding tool for requirement breakdown, generation, and iterative editing."),
            ],
            "prompt": "Write a keyboard-accessible tab component with three panels using plain HTML, CSS, and JavaScript. Explain how state changes work.",
        },
    },
    "doubao-seed-2-0-mini-260215": {
        "zh": {
            "tagline": "轻量任务快速响应",
            "summary": "面向重视响应延迟与处理成本的轻量任务，支持多模态理解和 256K 上下文。模型具备四档思考深度，可根据任务需求选择处理方式，适合简短交互、材料归纳及日常辅助工作。",
            "features": [
                ("轻量任务定位", "围绕响应速度与成本敏感的场景设计，适合频繁发生的简短处理任务。"),
                ("256K 上下文", "支持将较长材料纳入上下文，围绕给定内容开展理解与归纳。"),
                ("四档思考深度", "模型目录标注四档思考深度，便于按任务复杂度选择所需处理程度。"),
            ],
            "uses": [
                ("交互", "简短业务问答", "针对明确问题生成直接回答，用于需要及时反馈的轻量助手。"),
                ("长文", "材料重点归纳", "从较长说明或记录中找出重点，整理成便于继续处理的摘要。"),
                ("流程", "常规文本处理", "完成日常分类、改写与信息整理，把复杂分析留给后续专门环节。"),
            ],
            "prompt": "把这条客服回复改写得简洁礼貌：我们已经收到你的退货申请，请在包裹中附上订单号，仓库验收后安排退款。",
        },
        "en": {
            "tagline": "Fast, lightweight assistance",
            "summary": "Designed for lightweight work where response time and processing cost matter. It offers multimodal understanding, a 256K context window, and four thinking-depth levels for matching the amount of reasoning to the task.",
            "features": [
                ("Lightweight workloads", "Targets frequent, concise tasks in applications sensitive to response latency and processing cost."),
                ("256K context", "Bring longer source material into context for focused understanding and summaries."),
                ("Four thinking depths", "The catalog lists four thinking-depth levels for choosing how much processing a task needs."),
            ],
            "uses": [
                ("Interaction", "Brief business answers", "Respond directly to clear questions in assistants that need timely feedback."),
                ("Documents", "Extract the main points", "Condense long descriptions or records into a summary for the next stage of work."),
                ("Operations", "Routine text processing", "Handle everyday classification, rewriting, and organization tasks."),
            ],
            "prompt": "Make this support reply concise and polite: We received your return request. Include your order number in the package. We will arrange a refund after the warehouse inspects the item.",
        },
    },
    "doubao-seed-1-6-250615": {
        "zh": {
            "tagline": "自适应思考",
            "summary": "结合深度思考、多模态理解与 GUI 操作，支持 256K 上下文。模型可按需开启或关闭深度思考，也可通过自适应模式根据提示词复杂度决定是否思考，适用于难度不一的日常任务。",
            "features": [
                ("自适应思考", "根据提示词复杂度判断是否启用深度思考，也支持按任务需要选择开启或关闭。"),
                ("长上下文理解", "支持 256K 上下文，为长材料分析与连续对话提供上下文空间。"),
                ("多模态与 GUI", "具备多模态理解和图形界面操作能力，可用于理解页面并安排交互任务。"),
            ],
            "uses": [
                ("助手", "混合难度问答", "在同一应用中处理简单咨询与较复杂的问题，围绕实际需要使用思考能力。"),
                ("文档", "长材料梳理", "在长文档或多轮对话中归纳重点，提取与当前问题相关的信息。"),
                ("界面", "GUI 任务辅助", "理解界面内容及目标，梳理完成页面操作所需的步骤。"),
            ],
            "prompt": "一个团队有三项任务：整理需求需一天，开发需三天且依赖需求，测试需一天且依赖开发。请给出最早完成时间与安排。",
        },
        "en": {
            "tagline": "Adaptive thinking",
            "summary": "Combines deep thinking, multimodal understanding, and GUI operation with a 256K context window. Thinking can be enabled or disabled as needed, while adaptive mode decides whether deeper reasoning is warranted by prompt complexity.",
            "features": [
                ("Adaptive reasoning", "Choose whether to use deep thinking or let adaptive mode decide based on the complexity of the prompt."),
                ("Long-context understanding", "Use a 256K context window for extended source material and continuing conversations."),
                ("Multimodality and GUI", "Understand multimodal information and work with graphical interface tasks."),
            ],
            "uses": [
                ("Assistants", "Questions of varying difficulty", "Handle simple inquiries and more complex problems within the same application."),
                ("Documents", "Organize long materials", "Find relevant information and summarize the key points in long documents or conversations."),
                ("Interfaces", "Assist GUI tasks", "Interpret the interface and objective, then organize the steps required to complete the interaction."),
            ],
            "prompt": "A project needs one day for requirements, three days for development after requirements, and one day for testing after development. Give the earliest completion time and schedule.",
        },
    },
    "doubao-seed-1-6-251015": {
        "zh": {
            "tagline": "四档思考深度",
            "summary": "通过 reasoning_effort 提供 minimal、low、medium、high 四种思考模式。可按任务控制整体输出长度，在回答质量、响应延迟和 token 开销之间进行选择。",
            "features": [
                ("四种思考模式", "支持 minimal、low、medium 和 high，便于区分轻量处理与需要更多思考的任务。"),
                ("控制输出展开程度", "通过思考深度选择压缩整体输出长度，让处理程度更贴合实际任务。"),
                ("按场景评估取舍", "可围绕回答质量、响应时间和 token 使用量评估不同思考模式。"),
            ],
            "uses": [
                ("分流", "按任务选择深度", "为常规摘要、条件分析等不同任务配置合适的思考程度。"),
                ("交互", "控制回答展开", "在明确需要简洁响应的流程中减少展开，并为复杂问题保留深入处理空间。"),
                ("评估", "比较思考配置", "使用相同业务样本比较各档模式的回答质量与使用开销。"),
            ],
            "prompt": "比较同步通知和异步消息队列在订单系统中的适用场景，用一张表列出响应、失败处理和运维方面的取舍。",
        },
        "en": {
            "tagline": "Choose the reasoning depth",
            "summary": "Offers four reasoning_effort modes: minimal, low, medium, and high. Adjustable depth is intended to manage total output length and help applications choose a balance of answer quality, response latency, and token use.",
            "features": [
                ("Four reasoning modes", "Choose minimal, low, medium, or high according to how much thinking the task calls for."),
                ("Manage output length", "Use thinking depth to control how far the response expands around a task."),
                ("Evaluate practical tradeoffs", "Compare answer quality, response time, and token use across the available modes."),
            ],
            "uses": [
                ("Routing", "Match depth to the task", "Use different reasoning settings for routine summaries and more involved conditional analysis."),
                ("Interaction", "Manage response detail", "Keep straightforward workflows concise while leaving room for deeper work on complex questions."),
                ("Evaluation", "Compare reasoning settings", "Run the same business examples across modes to assess quality and processing overhead."),
            ],
            "prompt": "Compare synchronous notifications and asynchronous message queues for an order system. Use a table to explain response behavior, failure handling, and operational tradeoffs.",
        },
    },
    "doubao-seed-1-6-flash-250828": {
        "zh": {
            "tagline": "低延迟多模态",
            "summary": "Seed 1.6 系列中侧重快速响应的版本，同时具备深度思考、多模态理解和 256K 上下文。适合对延迟较敏感的交互与视觉处理任务，在需要迅速理解材料并返回结果的应用中使用。",
            "features": [
                ("快速响应定位", "围绕对延迟敏感的应用场景设计，适用于需要及时反馈的交互过程。"),
                ("多模态与视觉", "结合多模态理解处理图片等内容，为视觉任务提供信息分析能力。"),
                ("思考与长上下文", "同时具备深度思考能力和 256K 上下文，支持带有较长背景材料的任务。"),
            ],
            "uses": [
                ("交互", "即时辅助问答", "为正在操作中的用户提供简明解释与提示，支持连续交互体验。"),
                ("视觉", "图片信息处理", "围绕用户提交的图片理解内容，回答与当前任务相关的问题。"),
                ("阅读", "快速定位信息", "根据给定问题在长材料中寻找相关信息，整理成简短回答。"),
            ],
            "prompt": "用两句话解释什么是浏览器缓存，并给出一个用户能理解的日常例子。",
        },
        "en": {
            "tagline": "Responsive multimodal assistance",
            "summary": "The Seed 1.6 variant focused on quick responses, with deep thinking, multimodal understanding, and a 256K context window. It targets latency-sensitive interactions and visual tasks that need timely interpretation and feedback.",
            "features": [
                ("Response speed focus", "Designed for applications where timely feedback matters to the interaction."),
                ("Multimodal and visual tasks", "Interpret images and other supported material to answer questions about visual information."),
                ("Thinking with long context", "Combine deep-thinking capability with a 256K context window for tasks with substantial background material."),
            ],
            "uses": [
                ("Interaction", "In-the-moment assistance", "Offer concise explanations and prompts while a user is working through a task."),
                ("Vision", "Image-based questions", "Interpret an uploaded image and answer questions relevant to the user's immediate goal."),
                ("Reading", "Locate relevant information", "Find information in longer material and return a focused answer to a specific question."),
            ],
            "prompt": "Explain browser caching in two sentences and include an everyday example a nontechnical user can understand.",
        },
    },
    "doubao-seed-1-6-thinking-250615": {
        "zh": {
            "tagline": "深入推理与分析",
            "summary": "Seed 1.6 系列的深度思考版本，重点覆盖编程、数学和逻辑推理。支持 256K 上下文，适合需要理解较长材料、推导复杂条件或组织深入分析的任务，让问题求解有足够的上下文基础。",
            "features": [
                ("深度推理", "围绕复杂问题分析条件与关系，适用于需要深入判断的任务。"),
                ("编程与数学", "强化编程、数学和逻辑推理能力，帮助处理需要推导或分析的工作。"),
                ("256K 上下文", "理解与生成较长内容，将充足的背景材料纳入分析过程。"),
            ],
            "uses": [
                ("逻辑", "约束条件分析", "分析相互关联的规则与条件，说明可行方案和推导依据。"),
                ("编程", "算法与代码分析", "解释算法选择，检查代码中的逻辑问题，并提出验证方法。"),
                ("长文", "深入材料解读", "结合较长背景材料分析核心问题，整理论据、结论和仍待核验的事项。"),
            ],
            "prompt": "解释二分查找的适用条件与边界处理，给出 Python 实现，并列出空数组、单元素和目标不存在时的测试。",
        },
        "en": {
            "tagline": "In-depth reasoning and analysis",
            "summary": "The deep-thinking Seed 1.6 variant focuses on coding, mathematics, and logical reasoning. A 256K context window supports work that involves lengthy source material, interacting constraints, or detailed analysis.",
            "features": [
                ("Deep reasoning", "Analyze the conditions and relationships behind questions that call for careful judgment."),
                ("Coding and mathematics", "Apply coding, mathematical, and logical reasoning abilities to problems that need analysis or derivation."),
                ("256K context", "Understand and generate longer content while retaining substantial background material in context."),
            ],
            "uses": [
                ("Logic", "Analyze interacting constraints", "Work through connected rules and explain the basis for a proposed solution."),
                ("Coding", "Review algorithms and logic", "Explain algorithm choices, examine logical issues in code, and suggest verification cases."),
                ("Documents", "Develop an in-depth analysis", "Use extensive background material to organize evidence, conclusions, and points that need checking."),
            ],
            "prompt": "Explain the prerequisites and boundary handling for binary search. Provide Python code and tests for an empty array, one element, and a missing target.",
        },
    },
    "doubao-seed-1-6-thinking-250715": {
        "zh": {
            "tagline": "视觉参与深度推理",
            "summary": "在深度思考基础上结合视觉理解，覆盖编程、数学和逻辑推理任务。适合问题线索同时来自文字与图像的场景，可将图片中的内容纳入分析过程，辅助理解题目、图表及其他视觉材料。",
            "features": [
                ("增强思考能力", "围绕较复杂的问题组织分析，关注条件关系与结论依据。"),
                ("编程与逻辑", "结合编程、数学和逻辑推理能力，处理需要检查或推导的任务。"),
                ("视觉理解", "将图像内容纳入问题理解，连接视觉信息与文本推理。"),
            ],
            "uses": [
                ("学习", "图文问题解析", "结合题目文字和图片内容解释解题思路，指出求解所需条件。"),
                ("分析", "图表与逻辑判断", "读取视觉材料中的信息，结合文字背景分析关系与结论。"),
                ("研发", "带视觉线索的排查", "结合问题描述与可见界面信息，帮助梳理代码或逻辑层面的排查方向。"),
            ],
            "prompt": "一个数组中的数均为正整数。解释如何用滑动窗口找到和至少为目标值的最短连续子数组，并说明边界情况。",
        },
        "en": {
            "tagline": "Visual context for deep reasoning",
            "summary": "Combines stronger thinking with visual understanding for coding, mathematics, and logic tasks. It can bring image content into the analysis when a problem's clues are spread across written and visual material.",
            "features": [
                ("Enhanced thinking", "Organize analysis of more involved problems around their conditions and supporting evidence."),
                ("Coding and logic", "Apply programming, mathematical, and logical reasoning to tasks that need checking or derivation."),
                ("Visual understanding", "Include image content in problem interpretation and connect it with written reasoning."),
            ],
            "uses": [
                ("Learning", "Work through visual problems", "Use a problem's text and image to explain the approach and identify required conditions."),
                ("Analysis", "Reason about charts", "Read visual information alongside its written context to examine relationships and conclusions."),
                ("Engineering", "Investigate visual clues", "Combine a problem description and visible interface details to organize debugging directions."),
            ],
            "prompt": "For an array of positive integers, explain how a sliding window finds the shortest contiguous subarray whose sum reaches a target. Cover the edge cases.",
        },
    },
    "doubao-seed-1-6-vision-250815": {
        "zh": {
            "tagline": "视觉理解与推理",
            "summary": "侧重视觉深度思考，将多模态理解与推理用于教育、图像审查、巡检和搜索问答等场景。模型支持 256K 上下文及最高 64K tokens 输出，适合围绕图像信息组织较完整的分析。",
            "features": [
                ("视觉深度思考", "围绕图像中的内容、关系与文字进行理解，并结合任务要求展开分析。"),
                ("多模态推理", "连接视觉线索与其他上下文，用于教育、图像审查和搜索问答等工作。"),
                ("长上下文与输出", "支持 256K 上下文，最高输出长度为 64K tokens，为较完整的分析提供空间。"),
            ],
            "uses": [
                ("教育", "图像辅助讲解", "结合题目或示意图解释相关内容，帮助组织图文学习材料。"),
                ("巡检", "图片辅助审查", "按给定检查项整理图片中的可见信息，生成供人员复核的观察记录。"),
                ("搜索", "围绕图像问答", "以图片信息为线索回答具体问题，并结合提供的背景补充说明。"),
            ],
            "prompt": "为设备巡检照片设计一份观察清单，包含可见部件、状态描述、图片无法确认的事项和人工复核建议。",
        },
        "en": {
            "tagline": "Vision understanding and reasoning",
            "summary": "A visual deep-thinking model for education, image review, inspection, and search-based Q&A. It combines multimodal understanding with reasoning, a 256K context window, and a maximum output length of 64K tokens.",
            "features": [
                ("Visual deep thinking", "Interpret image content, relationships, and visible text in the context of the task."),
                ("Multimodal reasoning", "Connect visual clues with other context for educational, review, and question-answering workflows."),
                ("Long context and output", "Use a 256K context window and up to 64K output tokens for substantial analysis."),
            ],
            "uses": [
                ("Education", "Explain visual material", "Work with a problem image or diagram to organize an explanation and supporting learning material."),
                ("Inspection", "Assist image review", "Record visible details against a checklist and prepare observations for human review."),
                ("Search", "Answer image-based questions", "Use image details as the basis for focused answers, supported by supplied background information."),
            ],
            "prompt": "Design an observation checklist for equipment inspection photos. Include visible components, condition descriptions, details the image cannot establish, and human review suggestions.",
        },
    },
}
