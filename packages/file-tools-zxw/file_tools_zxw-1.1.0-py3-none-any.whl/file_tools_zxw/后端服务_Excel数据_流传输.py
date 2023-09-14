"""
# File       : 后端服务_Excel数据_流传输.py
# Time       ：2023/9/14 08:26
# Author     ：xuewei zhang
# Email      ：jingmu_predict@qq.com
# version    ：python 3.8
# Description：
"""
import xlwt
from io import BytesIO
from fastapi.responses import StreamingResponse


def export_exl(header, data, data_col, file_name='download.xlsx', need_order=False):
    """
    以流的形式导出到excel
    :param header: ['列名1', '列名2']
    :param data: [{'a': 1, 'b': 2}]			数据集，与header、data_col对应
    :param data_col: ['与列名对应的字段1', '与列名对应的字段2']
    :param file_name:
    :param need_order:
    :return:
    """

    def set_style():
        """
        设置样式
        :return:
        """
        # 居中设置
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER

        # 设置表头字体样式
        head_style = xlwt.XFStyle()
        font = xlwt.Font()
        font.name = 'Times New Roman'  # 字体
        font.bold = True  # 字体加粗
        font.height = int(15 * 10 * 2 * 1.3)
        head_style.font = font  # 设置字体
        head_style.alignment = alignment  # Add Alignment to Style

        # 设置表中内容样式
        cont_style = xlwt.XFStyle()
        font = xlwt.Font()
        font.name = 'Times New Roman'  # 字体
        font.bold = False  # 字体加粗
        font.height = 15 * 10 * 2
        cont_style.font = font  # 设置字体
        cont_style.alignment = alignment  # Add Alignment to Style

        # 设置单元格边界
        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        head_style.borders = borders
        cont_style.borders = borders
        return head_style, cont_style

    def get_sheet(_book, _index):
        """
        创建sheet页
        :param _book:
        :param _index:
        :return:
        """
        _name = "sheet_{}".format(str(_index))
        _sheet = _book.add_sheet(_name)
        return _sheet

    def write_head(_head, _sheet, _head_style):
        """
        写入表头
        :param _head:
        :param _sheet:
        :param _head_style:
        :return:
        """
        for head in range(len(header)):
            context = str(header[head])
            need_width = (1 + len(context)) * 256
            if need_width < 4500:
                need_width = 4500
            table_sheet.col(head).width = need_width
            table_sheet.write(0, head, context, style=_head_style)

    # 是否插入序号
    if need_order:
        header.insert(0, '序号')

    sheet_index = 1
    book = xlwt.Workbook(encoding='utf-8')  # 创建 Excel 文件
    table_sheet = get_sheet(book, sheet_index)  # 添加sheet表
    h_style, c_style = set_style()
    write_head(header, table_sheet, h_style)

    # 插入数据
    row = 1
    for item in data:
        if need_order:
            table_sheet.write(row, 0, row, style=c_style)  # 写入序号
            for col in range(len(header[1:])):
                table_sheet.write(
                    row, col + 1, str(item.get(data_col[col], '-') if item.get(data_col[col]) else '-'), style=c_style)
        else:
            for col in range(len(header)):
                table_sheet.write(
                    row, col, str(item.get(data_col[col], '-') if item.get(data_col[col]) else '-'), style=c_style)
        row += 1

        if row > 50000:  # 单表数量超过 65535 条 添加新的表
            row = 1
            sheet_index += 1
            table_sheet = get_sheet(book, sheet_index)  # 添加sheet表
            write_head(header, table_sheet, h_style)

    sio = BytesIO()  # 返回文件流到浏览端下载，浏览端必须以form提交方式方能下载成功！
    book.save(sio)  # 这点很重要，传给save函数的不是保存文件名，而是一个StringIO流
    sio.seek(0)  # 保存流
    # 组装header
    headers = {"content-type": "application/vnd.ms-excel",
               "content-disposition": f'attachment;filename={file_name}'}
    # 以流的形式返回浏览器
    return StreamingResponse(sio, media_type='xls/xlsx', headers=headers)
