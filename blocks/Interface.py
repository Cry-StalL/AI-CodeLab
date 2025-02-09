import re
import gradio as gr
from gradio_codeextend import CodeExtend as gr_CodeExtend
from core.code_execution.run_code import run_code

class Interface:
    def __init__(self):
        self._nav_items = {
            "📝 代码生成": ["从描述生成", "代码补全"],
            "🔍 代码解释": ["生成代码说明", "生成代码注释"],
            "⚡ 代码增强": ["错误修复", "代码优化"],
            "✅ 代码测试": ["测试用例生成"]
        }
        # 下面包含了Gradio中Code组件支持的所有语言
        self._lang_map = {
            # 通用编程语言
            'Python': 'python',
            'C': 'c',
            'C++': 'cpp',
            'Go': 'go',
            'Java': 'java',
            'R': 'r',
            'Rust': 'rust',

            # Web前端
            'HTML': 'html',
            'CSS': 'css',
            'SCSS': 'scss',
            'Vue': 'vue',

            # 标记语言/数据格式
            'Dockerfile': 'dockerfile',
            'Liquid': 'liquid',
            'Markdown': 'markdown',
            'JSON': 'json',
            'XML': 'xml',
            'YAML': 'yaml',

            # 脚本语言
            'Batch(Shell)': 'shell',
            'JavaScript': 'javascript',
            'Jinja2': 'jinja2',
            'PHP': 'php',
            'TypeScript': 'typescript',

            # SQL及其方言
            'SQL': 'sql',
            'Microsoft SQL': 'sql-msSQL',
            'MySQL': 'sql-mySQL',
            'MariaDB': 'sql-mariaDB',
            'SQLite': 'sql-sqlite',
            'Cassandra Query Language (CQL)': 'sql-cassandra',
            'PL/SQL': 'sql-plSQL',
            'HiveQL': 'sql-hive',
            'PL/pgSQL': 'sql-pgSQL',
            'GraphQL': 'sql-gql',
            'Greenplum SQL': 'sql-gpSQL',
            'Spark SQL': 'sql-sparkSQL',
            'Esper EPL': 'sql-esper'
        }
        self._lang_support_execution = {
            'Python',
        }
        self._model_list = [
            "DeepSeek-R1-Distill-Qwen-32B",
            "qwen-max",
            "qwen-plus",
            "qwen-turbo",
        ]

        # 控件
        self.btn_config = None
        self.btn_upload = None
        self.lang_selector = None
        self.model_selector = None
        self.editor = None
        self.nav_radio_components = []  # 左侧导航栏的所有radio控件
        self.run_button = None
        self.code_output_box = None

        # 测试用例生成相关控件（初始隐藏）
        self.testcase_button = None
        self.testcase_output_box = None
        self.import_button = None
        self.run_button2 = None
        self.spinner_html = None

        # 存储当前界面状态
        self.selected_feature = ""
        self.selected_language = ""
        self.selected_model = ""

    # ---------------- 公有接口-----------------#
    def create(self):
        with gr.Blocks() as block:
            gr.HTML(
                """
                <style>
                .loader {
                    border: 8px solid #f3f3f3;
                    border-top: 8px solid #3498db;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    animation: spin 1.5s linear infinite;
                    margin: auto;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .spinner-container {
                    text-align: center;
                }
                </style>
                """
            )

            with gr.Row():
                with gr.Column(scale=1, min_width=245, variant="compact"):
                    # left panel (navigation bar)
                    gr.Markdown("### 🧭 功能导航")

                    self.nav_radio_components = []

                    for category, items in self._nav_items.items():
                        radio = gr.Radio(
                            choices=items,
                            label=category,
                        )
                        self.nav_radio_components.append(radio)

                    self.btn_config = gr.Button("⚙️ 设置", size="md")
                    self.btn_upload = gr.Button("上传代码文件", size="md")

                with gr.Column(scale=9, min_width=800):
                    with gr.Row():
                        self.lang_selector = gr.Dropdown(
                            label="请选择编程语言",
                            choices=list(self._lang_map.keys()),
                            interactive=True,
                            filterable=True,
                            value=None
                        )
                        self.model_selector = gr.Dropdown(
                            label="请选择使用的模型",
                            choices=self._model_list,
                            interactive=True,
                            filterable=True,
                            value=None
                        )
                    # code editor
                    with gr.Row():
                        self.editor = gr_CodeExtend(lines=27, max_lines=27, interactive=True)
                    with gr.Row():
                        self.run_button = gr.Button(value="运行代码", variant="primary")
                        self.code_output_box = gr.Textbox(
                            label="代码输出",
                            interactive=False,
                            lines=8,
                            max_lines=8,
                            show_label=True,
                            show_copy_button=True
                        )

            with gr.Row():
                # toolbox
                with gr.Column():
                    gr.Markdown("### 🔧 功能区")

                    # 测试用例生成区域（默认隐藏）
                    with gr.Column(
                            visible=False) as testcase_column:  # 由原来的 gr.Row 改为 gr.Column，命名由 testcase_row 改为 testcase_column

                        with gr.Row():
                            with gr.Column(scale=1):
                                self.testcase_button = gr.Button("生成测试用例", variant="primary")
                            with gr.Column(scale=1):
                                self.testcase_run_button = gr.Button("运行代码", variant="primary")
                            with gr.Column(scale=1):
                                self.import_button = gr.Button("导入并运行", variant="secondary")

                        with gr.Row():
                            self.testcase_output_box = gr.Markdown(label="生成的测试用例")

                    # 绑定“生成测试用例”按钮事件，返回大模型结果
                    self.testcase_button.click(
                        fn=self._handle_testcase_generation,
                        inputs=[self.editor, self.model_selector, self.lang_selector],
                        outputs=self.testcase_output_box,
                    )
                    # 绑定“导入”按钮事件：将测试用例中的代码提取到代码编辑器中，并运行~
                    self.import_button.click(
                        fn=self._handle_import_testcase,
                        inputs=self.testcase_output_box,
                        outputs=[self.editor, self.code_output_box]
                    )
                    # 就是运行
                    self.testcase_run_button.click(
                        fn=self._handle_run_button_click_visible,
                        inputs=self.editor,
                        outputs=self.code_output_box
                    )

            # 加了个对测试用例生成区域的显示隐藏控制
            for radio in self.nav_radio_components:
                radio.select(
                    fn=self._handle_nav_selection,
                    inputs=radio,
                    outputs=[*self.nav_radio_components, testcase_column, self.run_button, self.code_output_box],
                )

            self.lang_selector.change(
                fn=self._handle_lang_selection,
                inputs=self.lang_selector,
                outputs=[self.editor, self.run_button],
            )

            self.model_selector.change(
                fn=self._handle_model_selection,
                inputs=self.model_selector,
            )

            self.run_button.click(
                fn=self._handle_run_button_click,
                inputs=self.editor,
                outputs=self.code_output_box
            )

    def get_feature(self) -> str:
        """
        获取用户当前在左侧导航栏选择的功能名称（与界面上的文本相同，是中文）。

        Returns:
            str: 当前选择的功能名称。
            未选择功能时，返回空字符串。
        """
        return self.selected_feature

    def get_language(self) -> str:
        """
        获取用户当前选择的编程语言名称（与界面上的文本相同）。

        Returns:
            str: 当前选择的编程语言名称。
            未选择编程语言时，返回空字符串。
        """
        return self.selected_language

    def get_model(self) -> str:
        """
        获取用户当前选择的模型名称（与界面上的文本相同）。

        Returns:
            str: 当前选择的模型名称。
            未选择模型时，返回空字符串。
        """
        return self.selected_model

    # ----------------私有方法-----------------#
    def _handle_nav_selection(self, selected_item: str):  # 导航栏按钮选中事件的handler
        """处理导航选择事件：选中一个时自动取消其他分类的选择"""
        self.selected_feature = selected_item
        radio_components_update = []
        for category, items in self._nav_items.items():
            if selected_item in items:
                radio_components_update.append(gr.update(value=selected_item))
            else:
                radio_components_update.append(None)
        # 当选择的是“测试用例生成”时，显示测试用例生成区域，否则隐藏
        if selected_item == "测试用例生成":
            testcase_update = gr.update(visible=True)
            run_btn_update = gr.update(visible=False)
            code_output_update = gr.update(visible=False)
        else:
            testcase_update = gr.update(visible=False)
            run_btn_update = gr.update(visible=True)
            code_output_update = gr.update(visible=True)
        radio_components_update.append(testcase_update)
        radio_components_update.append(run_btn_update)
        radio_components_update.append(code_output_update)
        return radio_components_update

    def _handle_lang_selection(self, selected_item: str):
        self.selected_language = selected_item

        code_update = gr.update(language=self._lang_map[selected_item])

        if self.get_language() in self._lang_support_execution:
            run_btn_update = gr.update(interactive=True, value="运行代码")
        else:
            run_btn_update = gr.update(interactive=False, value="该语言暂不支持在线运行")

        return code_update, run_btn_update

    def _handle_model_selection(self, selected_item: str):
        self.selected_model = selected_item

    def _handle_run_button_click(self, code):
        output = run_code(self.get_language(), code)
        return output

    def merge_chunk(self, accumulated: str, new_chunk: str) -> str:
        max_overlap = 0
        for i in range(1, min(len(accumulated), len(new_chunk)) + 1):
            if accumulated.endswith(new_chunk[:i]):
                max_overlap = i
        return accumulated + new_chunk[max_overlap:]

    def _handle_testcase_generation(self, code, model, language):
        """
        使用大模型生成测试用例：
        根据用户选择的编程语言和大模型，将代码发送给大模型，
        大模型返回的内容仅为测试用例代码，并以 markdown 形式展示。
        """
        if not code.strip():
            yield "代码为空！"
            return
        if not model:
            yield "请先选择大模型"
            return
        if not language:
            yield "请先选择编程语言"
            return

            # 显示动画和提示
        spinner_html = (
            "<div class='spinner-container'>"
            "<h3>测试用例正在生成，请稍后...</h3>"
            "<div class='loader'></div>"
            "</div>"
        )
        yield spinner_html

        prompt = (
            f"你是一位专业的软件测试工程师。请根据下面给出的{language}代码"
            f"编写测试用例（函数），覆盖主要功能和可能的边界情况；"
            f"仅输出测试的函数，供用户调用，不要额外解释。如果需要可以使用assert等测试函数"
            f"\n目标代码: \n{code}"
            f"最后把一定要输出测试用例、目标代码、调用测试用例的命令和通过测试的提醒！确保让用户可以直接运行"
            f"所有都要用中文注释，但是通过的提醒需要用英文"
        )
        from chat import ChatUI
        chat_ui = ChatUI()
        generator = chat_ui.gradio_interface(model, prompt)
        result = ""
        for chunk in generator:
            result = self.merge_chunk(result, chunk)

        yield result

    def _handle_import_testcase(self, testcase_content: str):
        """
        处理“导入”按钮点击事件：
         - 从Markdown文本中提取代码块内容（如果有用 ``` 包裹），
         - 否则直接复制全部内容，
         - 更新代码编辑器的内容。
        """
        code_blocks = re.findall(r"```(?:\w*\n)?(.*?)```", testcase_content, re.DOTALL)
        if code_blocks:
            code = "\n".join(code_blocks).strip()
        else:
            code = testcase_content.strip()
        # 自动运行代码
        output = run_code(self.get_language(), code)
        # 返回两个更新：更新编辑器内容，更新并显示“代码输出”框
        return gr.update(value=code), gr.update(visible=True, value=output)

    def _handle_run_button_click_visible(self, code):
        output = run_code(self.get_language(), code)
        return gr.update(visible=True, value=output)

interface = Interface()
