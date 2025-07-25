import streamlit as st
import PyPDF2
import io
import os
from datetime import datetime
import zipfile


def process_pdf(uploaded_file):
    # 读取上传的PDF文件
    pdf_reader = PyPDF2.PdfReader(uploaded_file)

    # 创建一个新的PDF写入器
    pdf_writer = PyPDF2.PdfWriter()

    # 只添加第一页
    if len(pdf_reader.pages) > 0:
        pdf_writer.add_page(pdf_reader.pages[0])

    # 创建输出的字节流
    output_bytes = io.BytesIO()
    pdf_writer.write(output_bytes)
    output_bytes.seek(0)

    return output_bytes


def create_zip_file(pdf_files_data):
    # 创建一个内存中的ZIP文件
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for original_name, pdf_data in pdf_files_data:
            # 构建新文件名（first_page_原文件名）
            new_filename = f"{original_name}"
            # 将PDF添加到ZIP文件中
            zip_file.writestr(new_filename, pdf_data.getvalue())

    zip_buffer.seek(0)
    return zip_buffer


def main():
    st.title("PDF 首页提取器")
    st.write("上传PDF文件，程序将只保留第一页")

    # 添加使用说明
    with st.expander("📖 使用说明", expanded=True):
        st.markdown(
            """
        ### 如何使用：
        1. 点击"选择PDF文件"按钮
        2. 您可以：
           - 按住 Ctrl 键（Windows）或 Command 键（Mac）选择多个文件
           - 直接拖拽多个PDF文件到上传区域
        3. 选择下载方式：
           - 单个下载：每个文件单独下载
           - 打包下载：所有文件打包成zip下载
        """
        )

    uploaded_files = st.file_uploader(
        "选择PDF文件", type="pdf", accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"### 已上传 {len(uploaded_files)} 个文件")

        # 处理所有PDF文件并保存结果
        processed_files = []
        for uploaded_file in uploaded_files:
            output_pdf = process_pdf(uploaded_file)
            processed_files.append((uploaded_file.name, output_pdf))

        # 添加打包下载按钮
        if len(uploaded_files) > 1:
            zip_buffer = create_zip_file(processed_files)
            st.download_button(
                label="⬇️ 打包下载所有文件 (ZIP)",
                data=zip_buffer,
                file_name="first_pages.zip",
                mime="application/zip",
            )

            st.divider()
            st.write("### 或者单独下载各个文件：")

        # 创建三列布局显示单个文件
        col1, col2, col3 = st.columns(3)

        # 使用循环将文件平均分配到三列中
        for idx, (original_name, pdf_data) in enumerate(processed_files):
            with [col1, col2, col3][idx % 3]:
                with st.container():
                    st.write(f"📄 {original_name}")

                    # 构建新文件名
                    new_filename = f"{original_name}"

                    # 创建下载按钮
                    st.download_button(
                        label=f"⬇️ 下载文件",
                        data=pdf_data,
                        file_name=new_filename,
                        mime="application/pdf",
                    )
                    st.divider()


if __name__ == "__main__":
    main()
