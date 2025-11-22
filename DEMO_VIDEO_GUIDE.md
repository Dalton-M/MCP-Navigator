# Demo 视频录制指南

本指南帮助你录制一个出色的 hackathon demo 视频，展示 MCP Stack Composer 的完整功能。

## 视频要求

- **时长**: 1-2 分钟
- **格式**: MP4 (推荐), MOV, or WebM
- **分辨率**: 1080p (1920x1080) 推荐
- **音频**: 清晰的旁白或字幕

---

## 视频结构（90 秒版本）

### 第 1 部分：介绍（10 秒）
- 项目名称展示
- 一句话说明价值主张

### 第 2 部分：问题陈述（10 秒）
- 展示当前 MCP 集成的痛点
- 为什么需要自动化的 MCP 编排

### 第 3 部分：解决方案演示（50 秒）
- 实时运行 MCP Stack Composer
- 展示完整的 4 步流程

### 第 4 部分：技术亮点（15 秒）
- 强调使用的技术栈
- Groq + Docker MCP Hub + E2B

### 第 5 部分：总结与 CTA（5 秒）
- 项目 GitHub 链接
- 邀请试用

---

## 详细脚本

### 开场（0:00 - 0:10）

**画面**: 标题屏幕或终端准备界面

**旁白**: 
> "Hi! 我是 [你的名字]，这是 MCP Stack Composer - 一个智能的 MCP 服务器编排工具，由 Groq、Docker MCP Hub 和 E2B 驱动。"

**文字叠加**:
```
🚀 MCP Stack Composer
Powered by Groq + Docker MCP Hub + E2B
```

---

### 问题场景（0:10 - 0:20）

**画面**: 展示一个复杂的 MCP 配置文件或手动配置过程

**旁白**:
> "构建 AI agents 时，选择合适的 MCP 服务器并正确配置它们是个挑战。你需要理解每个 MCP 的能力、配置环境变量、编写集成代码..."

**文字叠加**:
```
😓 The Challenge:
- 选择合适的 MCP 服务器？
- 如何配置和集成？
- 手动编写样板代码...
```

---

### 解决方案演示（0:20 - 1:10）

**画面**: 实时运行程序

#### Step 1: 输入需求（0:20 - 0:30）

**操作**: 启动程序并输入需求

```bash
$ python3 run.py
```

**输入**:
```
I want an agent that reads GitHub issues, searches the web for similar solutions, and posts a daily summary.
```

**旁白**:
> "只需用自然语言描述你的需求..."

---

#### Step 2: Groq 分析（0:30 - 0:40）

**画面**: 显示 Groq 提取的 capabilities

**旁白**:
> "Groq 的 LLM 自动分析需求，提取结构化的能力标签..."

**文字叠加**:
```
🎯 Groq 智能分析
Capabilities: code_hosting.read_issues, web_search, notify.slack
```

---

#### Step 3: MCP 匹配（0:40 - 0:50）

**画面**: 显示推荐的 MCP 列表

**旁白**:
> "系统从 Docker MCP Hub 匹配最合适的 MCP 服务器..."

**文字叠加**:
```
🔧 推荐的 MCP:
1. GitHub Official MCP
2. Brave Search MCP
3. Slack MCP
```

---

#### Step 4: 代码生成（0:50 - 1:00）

**画面**: 展示生成的环境配置和代码片段

**旁白**:
> "Groq 自动生成完整的配置说明和可运行的代码..."

**快速滚动展示**:
- 环境变量配置
- Docker 运行命令
- Python 代码示例

---

#### Step 5: 实时调用（1:00 - 1:10）

**画面**: 展示真实的 MCP 调用结果

**旁白**:
> "最后，实时调用 MCP 服务器，展示实际的集成效果！"

**文字叠加**:
```
✨ Live Demo
Real GitHub API call → 3 issues fetched
```

---

### 技术亮点（1:10 - 1:25）

**画面**: 分屏或快速切换展示技术栈

**旁白**:
> "整个流程运行在 E2B 云沙盒中，使用 Groq 进行快速 LLM 推理，连接 Docker MCP Hub 的 10+ 个 MCP 服务器。"

**文字叠加**:
```
💡 技术栈:
✓ E2B - 云端沙盒环境
✓ Groq - 超快 LLM 推理
✓ Docker MCP Hub - 10+ MCP 服务器
✓ Python + Rich CLI
```

---

### 结尾（1:25 - 1:30）

**画面**: 项目 logo 和链接

**旁白**:
> "MCP Stack Composer - 让 AI agent 开发更简单。立即试用！"

**文字叠加**:
```
🔗 Try it now:
github.com/YOUR_USERNAME/mcp-stack-composer

⭐ Star us on GitHub!
```

---

## 录制技巧

### 工具推荐

**macOS:**
- QuickTime Player (内置)
- ScreenFlow (专业)
- OBS Studio (免费开源)

**Windows:**
- OBS Studio (免费开源)
- Camtasia (专业)

**Linux:**
- OBS Studio
- SimpleScreenRecorder
- Kazam

### 录制设置

1. **分辨率**: 1920x1080 (1080p)
2. **帧率**: 30 fps 或 60 fps
3. **音频**: 使用外接麦克风（如果可能）
4. **背景音乐**: 可选，但音量要低

### 终端美化

```bash
# 使用 Rich 的输出已经很漂亮了
# 如果需要，可以调整终端主题

# macOS Terminal 设置
- Font: Monaco 14pt 或 Menlo 14pt
- Theme: 深色主题（Pro 或 Basic）
- Window size: 120 x 30

# 确保文字清晰可读
```

### 光标和鼠标

- 使用大光标（便于观看）
- 鼠标移动不要太快
- 突出显示重要部分

---

## 后期编辑

### 基础编辑

1. **裁剪**: 移除开头和结尾的多余内容
2. **加速**: 某些步骤可以 1.5x 或 2x 加速
3. **字幕**: 添加关键点的文字说明

### 建议的加速点

- 依赖安装过程: 2x 速度或跳过
- 长输出滚动: 1.5x 速度
- 代码生成输出: 快速滚动展示

### 文字叠加

添加文字说明在以下时刻：
- 技术栈展示
- 关键步骤标题
- GitHub 链接
- 重要结果数据

### 音乐建议

- 使用无版权音乐（YouTube Audio Library, Epidemic Sound）
- 保持音量低于旁白（-20dB 到 -30dB）
- 选择节奏明快但不喧宾夺主的背景音

---

## 录制前检查清单

- [ ] 测试程序运行正常
- [ ] API keys 已配置（如果演示真实调用）
- [ ] 终端字体大小合适（14pt+）
- [ ] 桌面整洁（关闭无关窗口）
- [ ] 麦克风音量测试
- [ ] 网络连接稳定
- [ ] 准备好演示用的输入文本
- [ ] 预演 1-2 次

---

## 录制脚本模板

创建一个 `demo_input.txt` 文件：

```
I want an agent that reads GitHub issues, searches the web for similar solutions, and posts a daily summary.
```

录制时使用：
```bash
cat demo_input.txt | python3 run.py
```

这样可以避免现场打字错误。

---

## B-Roll 素材建议

除了主演示，可以录制额外素材：

1. **代码特写**: 展示关键代码片段
2. **架构图**: 如果有的话
3. **E2B Dashboard**: 显示云端运行状态
4. **Groq Console**: 显示 API 使用情况
5. **Docker MCP Hub**: 浏览 MCP 目录

---

## 发布检查清单

录制完成后：

- [ ] 视频时长符合要求（1-2 分钟）
- [ ] 音频清晰无杂音
- [ ] 画面清晰，文字可读
- [ ] 包含项目名称和链接
- [ ] 展示了完整的 4 步流程
- [ ] 突出了 E2B + Groq + MCP Hub
- [ ] 有明确的 Call-to-Action
- [ ] 文件大小合理（< 100MB）

---

## 替代方案：Slide + Voice Over

如果不方便录制实时演示：

1. **准备 PPT/Keynote**
   - Slide 1: 标题 + 价值主张
   - Slide 2: 问题场景
   - Slide 3-6: 流程截图（4 个步骤）
   - Slide 7: 技术栈
   - Slide 8: CTA

2. **截图准备**
   - 高清截图每个步骤的输出
   - 添加标注和箭头
   - 突出显示关键信息

3. **录制 Voice Over**
   - 使用 Loom 或 QuickTime
   - 按脚本讲解每页 slides

---

## 示例脚本（完整版）

```
[0:00] Hi, I'm [Name], and this is MCP Stack Composer.

[0:05] Building AI agents? Choosing and configuring MCP servers is complex.

[0:10] Watch this. I describe my agent in plain English...

[0:15] Groq's LLM analyzes it and extracts capability tags.

[0:25] The system matches MCPs from Docker Hub automatically.

[0:35] Groq generates complete setup instructions and code.

[0:45] And finally, a live MCP call - real GitHub issues fetched!

[0:55] All running in E2B cloud sandbox, powered by Groq,
      connected to 10+ Docker MCP servers.

[1:10] MCP Stack Composer - make AI agent development easier.
      Try it now at github.com/YOUR_USERNAME/mcp-stack-composer

[1:20] Star us on GitHub! Thank you!
```

---

## 提交清单

最后提交前：

- [ ] 视频文件命名: `mcp-stack-composer-demo.mp4`
- [ ] 缩略图（如果需要）: 关键画面截图
- [ ] 视频描述文本准备好
- [ ] YouTube/Vimeo 链接（如果要求）
- [ ] 备份视频文件

---

祝你录制顺利！🎬✨

