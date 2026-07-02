# VHS documentation
#
# Output:
#   Output <path>.gif               Create a GIF output at the given <path>
#   Output <path>.mp4               Create an MP4 output at the given <path>
#   Output <path>.webm              Create a WebM output at the given <path>
#
# Require:
#   Require <string>                Ensure a program is on the $PATH to proceed
#
# Settings:
#   Set FontSize <number>           Set the font size of the terminal
#   Set FontFamily <string>         Set the font family of the terminal
#   Set Height <number>             Set the height of the terminal
#   Set Width <number>              Set the width of the terminal
#   Set LetterSpacing <float>       Set the font letter spacing (tracking)
#   Set LineHeight <float>          Set the font line height
#   Set LoopOffset <float>%         Set the starting frame offset for the GIF loop
#   Set Theme <json|string>         Set the theme of the terminal
#   Set Padding <number>            Set the padding of the terminal
#   Set Framerate <number>          Set the framerate of the recording
#   Set PlaybackSpeed <float>       Set the playback speed of the recording
#   Set MarginFill <file|#000000>   Set the file or color the margin will be filled with.
#   Set Margin <number>             Set the size of the margin. Has no effect if MarginFill isn't set.
#   Set BorderRadius <number>       Set terminal border radius, in pixels.
#   Set WindowBar <string>          Set window bar type. (one of: Rings, RingsRight, Mac, MacRight, Colorful, ColorfulRight)
#   Set WindowBarSize <number>      Set window bar size, in pixels. Default is 40.
#   Set TypingSpeed <time>          Set the typing speed of the terminal. Default is 50ms.
#
# Sleep:
#   Sleep <time>                    Sleep for a set amount of <time> in seconds
#
# Type:
#   Type[@<time>] "<characters>"    Type <characters> into the terminal with a
#                                   <time> delay between each character
#
# Keys:
#   Escape[@<time>] [number]        Press the Escape key
#   Backspace[@<time>] [number]     Press the Backspace key
#   Delete[@<time>] [number]        Press the Delete key
#   Insert[@<time>] [number]        Press the Insert key
#   Down[@<time>] [number]          Press the Down key
#   Enter[@<time>] [number]         Press the Enter key
#   Space[@<time>] [number]         Press the Space key
#   Tab[@<time>] [number]           Press the Tab key
#   Left[@<time>] [number]          Press the Left Arrow key
#   Right[@<time>] [number]         Press the Right Arrow key
#   Up[@<time>] [number]            Press the Up Arrow key
#   Down[@<time>] [number]          Press the Down Arrow key
#   PageUp[@<time>] [number]        Press the Page Up key
#   PageDown[@<time>] [number]      Press the Page Down key
#   Ctrl+<key>                      Press the Control key + <key> (e.g. Ctrl+C)
#
# Display:
#   Hide                            Hide the subsequent commands from the output
#   Show                            Show the subsequent commands in the output

Output assets/demo.gif

Require echo

Set FontSize 18
Set Width 1200
Set Height 600
Set Theme "Dracula"
Set WindowBar Mac

Type "echo 'User: 我们要加个支付模块，赶紧把代码写出来。'"
Enter
Sleep 1s

Type "echo '🤖 guyue: 收到需求。正在启动古月分身架构审查...'"
Enter
Sleep 1s

Type "echo '[!] 意图拦截命中: system-design (架构优先)'"
Enter
Sleep 500ms

Type "echo '🔍 正在读取 memory-bank 历史踩坑记录...'"
Enter
Sleep 500ms

Type "echo '⚠️ 发现历史档案: .guyue_memory/202604_payment_callback_issue.md'"
Enter
Sleep 1s

Type "echo '---------------------------------------------------'"
Enter
Type "echo '💡 [古月架构设计方案]'"
Enter
Type "echo '由于是核心模块，支付逻辑必须收拢在后端，前端仅提供交互入口。'"
Enter
Type "echo '另外根据历史教训，必须增加异步对账兜底策略。'"
Enter
Type "echo '请确认方案，我再开始写代码：(Y/n)'"
Enter
Type "echo '---------------------------------------------------'"
Enter

Sleep 3s
