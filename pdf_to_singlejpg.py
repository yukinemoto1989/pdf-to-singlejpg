import flet as ft
import fitz  # PyMuPDF
import os

def main(page: ft.Page):
    page.title = "PDF → JPG 変換"
    page.window.width = 300
    page.window.height = 260
    page.window.min_width = 300
    page.window.min_height = 260
    page.window.max_width = 300
    page.window.max_height = 260

    # アプリアイコンの設定
    root_dir = os.path.dirname(os.path.abspath(__file__))
    page.window.icon = os.path.join(root_dir, "pdf_to_singlejpg.ico")

    # 状態表示
    status_text = ft.Text("PDFファイルと保存先を選択してください", size=14)
    progress_bar = ft.ProgressBar(width=260, visible=False)

    selected_pdf_path = None
    selected_output_dir = None

    def on_file_selected(e: ft.FilePickerResultEvent):
        nonlocal selected_pdf_path
        if e.files:
            selected_pdf_path = e.files[0].path
            status_text.value = f"選択されたPDF: {os.path.basename(selected_pdf_path)}"
            status_text.color = ft.colors.BLACK
        else:
            status_text.value = "PDFファイルの選択がキャンセルされました。"
            status_text.color = ft.colors.RED
        page.update()

    def on_folder_selected(e: ft.FilePickerResultEvent):
        nonlocal selected_output_dir
        if e.path:
            selected_output_dir = e.path
            status_text.value += f"\n保存先: {selected_output_dir}"
            status_text.color = ft.colors.BLACK
        else:
            status_text.value += "\n保存先の選択がキャンセルされました。"
            status_text.color = ft.colors.RED
        page.update()

    def on_convert_click(e):
        nonlocal selected_output_dir

        if not selected_pdf_path:
            status_text.value = "PDFファイルを選択してください。"
            status_text.color = ft.colors.RED
            page.update()
            return

        # 保存先が未指定ならPDFのフォルダに設定
        if not selected_output_dir:
            selected_output_dir = os.path.dirname(selected_pdf_path)

        try:
            doc = fitz.open(selected_pdf_path)
            base_name = os.path.splitext(os.path.basename(selected_pdf_path))[0]
            total_pages = len(doc)

            progress_bar.visible = True
            progress_bar.value = 0.0
            page.update()

            for i, page_obj in enumerate(doc):
                pix = page_obj.get_pixmap(dpi=200)
                output_path = os.path.join(selected_output_dir, f"{base_name}_page_{i+1}.jpg")
                pix.save(output_path)

                progress_bar.value = (i + 1) / total_pages
                status_text.value = f"{i+1}/{total_pages}ページ変換中..."
                status_text.color = ft.colors.BLACK
                page.update()

            status_text.value = f"{total_pages}ページの画像保存が完了しました。\n保存先: {selected_output_dir}"
        except Exception as ex:
            status_text.value = f"エラー: {ex}"
            status_text.color = ft.colors.RED

        progress_bar.visible = False
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    folder_picker = ft.FilePicker(on_result=on_folder_selected)

    file_button = ft.ElevatedButton("PDFを選択", on_click=lambda _: file_picker.pick_files(allowed_extensions=["pdf"]))
    folder_button = ft.ElevatedButton("保存先を選択", on_click=lambda _: folder_picker.get_directory_path())
    convert_button = ft.ElevatedButton("変換開始", on_click=on_convert_click)

    page.overlay.extend([file_picker, folder_picker])

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    status_text,
                    file_button,
                    folder_button,
                    convert_button,
                    progress_bar,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            padding=20,
            bgcolor=ft.colors.GREY_100,
            border_radius=10,
        )
    )

ft.app(target=main)
