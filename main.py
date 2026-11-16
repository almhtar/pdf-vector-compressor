import os
import shutil
import threading
import flet as ft

try:
    import vec_dedup
except Exception:
    vec_dedup = None


def main(page: ft.Page):
    page.title = "PDF Compressor"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 24
    page.theme_mode = ft.ThemeMode.DARK

    state = {
        "input_path": None,
        "output_path": None,
    }

    status_text = ft.Text(
        "Select a PDF file to start",
        size=15,
        text_align=ft.TextAlign.CENTER,
        selectable=True,
    )
    progress_ring = ft.ProgressRing(visible=False)

    file_picker = ft.FilePicker()
    share_service = ft.Share()
    page.services.extend([file_picker, share_service])

    async def handle_pick_file(e):
        files = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["pdf"],
        )
        if files and len(files) > 0:
            picked = files[0]
            if picked.path:
                state["input_path"] = picked.path
                state["output_path"] = None
                status_text.value = f"Selected: {picked.name}"
                compress_btn.disabled = False
                share_btn.visible = False
            else:
                status_text.value = "Error: Could not read file path"
                compress_btn.disabled = True
            page.update()

    async def handle_share_file(e):
        out_path = state["output_path"]
        if out_path and os.path.exists(out_path):
            try:
                await share_service.share_files(
                    [ft.ShareFile.from_path(out_path)],
                    text="Compressed PDF",
                )
            except Exception as ex:
                status_text.value = f"Share Error: {str(ex)}"
                page.update()

    def execute_compression(src, dst):
        if vec_dedup and hasattr(vec_dedup, "compress_pdf"):
            return vec_dedup.compress_pdf(src, dst)
        else:
            shutil.copy2(src, dst)
            return 0

    def run_compression_task():
        input_path = state["input_path"]
        if not input_path or not os.path.exists(input_path):
            status_text.value = "File not found!"
            progress_ring.visible = False
            compress_btn.disabled = False
            pick_btn.disabled = False
            page.update()
            return

        try:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            out_filename = f"{base_name}_compressed.pdf"
            target_folder = "/storage/emulated/0/Download/PDF_Compressed"

            try:
                os.makedirs(target_folder, exist_ok=True)
                output_path = os.path.join(target_folder, out_filename)
                templates_count = execute_compression(input_path, output_path)
            except PermissionError:
                output_path = os.path.join(os.path.dirname(input_path), out_filename)
                templates_count = execute_compression(input_path, output_path)

            state["output_path"] = output_path
            orig_size = os.path.getsize(input_path) / (1024 * 1024)
            new_size = os.path.getsize(output_path) / (1024 * 1024)

            status_text.value = (
                f"Done! (Templates: {templates_count})\n"
                f"Size: {orig_size:.2f} MB -> {new_size:.2f} MB\n\n"
                f"Saved at:\n{output_path}"
            )
            share_btn.visible = True
        except Exception as ex:
            status_text.value = f"Error: {str(ex)}"
        finally:
            progress_ring.visible = False
            compress_btn.disabled = False
            pick_btn.disabled = False
            page.update()

    def on_compress_click(e):
        progress_ring.visible = True
        compress_btn.disabled = True
        pick_btn.disabled = True
        share_btn.visible = False
        status_text.value = "Compressing PDF, please wait..."
        page.update()
        threading.Thread(target=run_compression_task, daemon=True).start()

    pick_btn = ft.Button(
        content="Choose PDF File",
        icon=ft.Icons.FOLDER_OPEN,
        on_click=handle_pick_file,
    )

    compress_btn = ft.Button(
        content="Compress PDF",
        icon=ft.Icons.COMPRESS,
        disabled=True,
        on_click=on_compress_click,
    )

    share_btn = ft.Button(
        content="Share Compressed PDF",
        icon=ft.Icons.SHARE,
        visible=False,
        on_click=handle_share_file,
    )

    page.add(
        ft.Icon(ft.Icons.PICTURE_AS_PDF, size=64, color=ft.Colors.RED_400),
        ft.Text("PDF Compressor", size=22, weight=ft.FontWeight.BOLD),
        ft.Divider(height=20),
        pick_btn,
        compress_btn,
        share_btn,
        progress_ring,
        status_text,
    )


ft.run(main)