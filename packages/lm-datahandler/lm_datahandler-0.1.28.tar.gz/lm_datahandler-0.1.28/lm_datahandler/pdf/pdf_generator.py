import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table, TableStyle, Image


def report_pdf_generator(pdf_save_path, Results):
    print(Results)
    print(pdf_save_path)
    # Intialization
    # 注册字体
    pdfmetrics.registerFont(TTFont("Yahei", "C:\Windows\Fonts\msyhbd.ttc"))
    # if os.path.isdir(pdf_save_path):
    #     pdf_save_path = os.path.join(pdf_save_path, "sleep_report.pdf")
    pdf_file = Canvas(pdf_save_path, pagesize=A4)
    # Results=os.path.join(PdfSavePath,"my_file.pdf")
    # plt.savefig(os.path.join(PdfSavePath,"TmpFigure.png"))
    # Create an Image object with the iterable object

    TFimg = Image(Results["sleep_plot"], width=495, height=420) if Results["sleep_plot"] is not None else Image(
        width=495, height=420)
    Description = "备注：\n" \
                  "断连率：因额贴与设备基座距离太远导致数据无法记录的时间占总记录时间的比例，大于5%可能对睡眠分析结果造成明显影响。\n" \
                  "丢包率：因夜间用户移动超出额贴与通信距离导致的蓝牙信号传输中断所带来的丢包。丢包率通常小于0.5%，大于5%可对睡眠指标造成明显影响。\n" \
                  "总记录时间（TRT）：从关灯到开灯的时间(先用开始记录/停止时间替代)，是睡眠记录的全部时长。\n" \
                  "总睡眠时间（TST）：关灯至开灯时间内实际睡眠时间总和，即各睡眠期（N1期，N2期，N3期，R期）时间的总和。\n" \
                  "入睡延迟（SOL）：从关灯（开始记录）到出现第一帧睡眠期的时间。\n" \
                  "入睡后清醒时间（WASO）/次数（AR）：从稳定的睡眠期到睡眠结束（最后一个睡眠周期）之间，所有的清醒时间的总和/清醒次数。\n" \
                  "睡眠效率（SE）：总睡眠时间/总记录时间×100％。\n" \
                  "各睡眠期比例：各睡眠期（N1/N2期，N3期，R期）分别累计的时间占总睡眠时间（不包括清醒时间）的百分比。\n" \
                  "睡眠分期图中，Abnormal一般表示未佩戴状态（接触不良或者脱落）或者存在较大干扰导致信号异常。"
    n3_time = Results.get("N3") if Results.get("N3") is not None else None
    n1n2_time = Results.get("N1/N2") if Results.get("N3") is not None else None
    rem_time = Results.get("REM") if Results.get("N3") is not None else None
    n3_rate = None
    n1n2_rate = None
    rem_rate = None
    if n3_time is not None and n1n2_time is not None and rem_time is not None:
        n3_time = n3_time if n3_time > 0 else 0
        n1n2_time = n1n2_time if n1n2_time > 0 else 0
        rem_time = rem_time if rem_time > 0 else 0
        total_time = n3_time + n1n2_time + rem_time
        if total_time == 0:
            n3_rate = "--"
            n1n2_rate = "--"
            rem_rate = "--"
        else:
            n3_rate = "{:.2f}%".format(n3_time / total_time * 100)
            n1n2_rate = "{:.2f}%".format(n1n2_time / total_time * 100)
            rem_rate = "{:.2f}%".format(rem_time / total_time * 100)

    phone_number = Results.get("phone_number") if Results.get("phone_number") is not None else "--"
    record_date = Results.get("record_date") if Results.get("record_date") is not None else "--"
    record_start_time = Results.get("record_start_time") if Results.get("record_start_time") is not None else "--"
    record_end_time = Results.get("record_end_time") if Results.get("record_end_time") is not None else "--"
    package_loss_rate = Results.get("package_loss_rate") if Results.get("package_loss_rate") is not None else "--"
    disconnection_rate = Results.get("disconnection_rate") if Results.get("disconnection_rate") is not None else "--"
    trt = "{:.2f}".format(Results.get("trt")) if Results.get("trt") is not None else "--"
    tst = "{:.2f}".format(Results.get("tst")) if Results.get("tst") is not None else "--"
    se = Results.get("se") if Results.get("se") is not None else "--"
    sl = Results.get("sl") if Results.get("sl") is not None else "--"
    if sl is not None:
        sl = "{:.2f}".format(sl) if sl > 0 else "--"

    data = [
        ["居家睡眠监测报告"],
        ["姓名", "XXXXX", "手机号", phone_number, "监测日期", record_date],

        ["记录时间"],
        ["记录开始时间", record_start_time, "", "记录结束时间", record_end_time],
        ["信号质量"],
        ["断连率(%)", disconnection_rate, "", "丢包率(%)", package_loss_rate, ""],
        ["睡眠综合分析图"],
        [TFimg],
        ["睡眠参数"],
        ["总记录时间(TRT,min)", trt, "", "总睡眠时间(TST,min)", tst],
        ["睡眠效率(SE,%)", se, "", "入睡延迟(SOL,min)", sl],
        ["入睡后清醒时间(WASO,min)", "{:.2f}".format(Results.get("waso")) if Results.get("waso") is not None else "--",
         "",
         "入睡后清醒次数(AR)", Results.get("ar") if Results.get("ar") is not None else "--"],

        ["各期睡眠时间(min)"],
        ["N3", n3_time, "N1/N2", n1n2_time, "REM", rem_time],
        ["各期睡眠比例(%)"],
        ["N3", n3_rate if n3_rate is not None else "--", "N1/N2", n1n2_rate if n1n2_rate is not None else "--", "REM",
         rem_rate if rem_rate is not None else "--"],
        [Description]
    ]
    SPAN_SPAN_SPAN_SPAN_ = [("SPAN", (0, 0), (-1, 0)),
                            ("SPAN", (0, 2), (-1, 2)),
                            ("SPAN", (0, 4), (-1, 4)),

                            ("SPAN", (0, 6), (-1, 6)),
                            ("SPAN", (0, 7), (-1, 7)),
                            ("SPAN", (0, 8), (-1, 8)),

                            # ("SPAN", (0, 10), (-1, 10)),
                            ("SPAN", (0, 12), (-1, 12)),
                            ("SPAN", (0, 14), (-1, 14)),
                            ("SPAN", (0, 16), (-1, 16)),

                            ("SPAN", (1, 3), (2, 3)),
                            ("SPAN", (-2, 3), (-1, 3)),

                            ("SPAN", (1, 5), (2, 5)),
                            ("SPAN", (-2, 5), (-1, 5)),

                            ("SPAN", (1, 9), (2, 9)),
                            ("SPAN", (-2, 9), (-1, 9)),

                            ("SPAN", (1, 10), (2, 10)),
                            ("SPAN", (-2, 10), (-1, 10)),

                            ("SPAN", (1, 11), (2, 11)),
                            ("SPAN", (-2, 11), (-1, 11)),

                            # ("SPAN", (9, 2), (11, 2)),
                            # ("SPAN", (9, 5), (11, 5)),

                            # ("SPAN", (1, 7), (2, 7)),
                            # ("SPAN", (4, 7), (5, 7)),
                            # ("SPAN", (1, 8), (2, 8)),
                            # ("SPAN", (4, 8), (5, 8)),
                            #
                            #
                            # ("SPAN", (0, 8), (-1, 8)),
                            # ("SPAN", (1, 9), (2, 9)),
                            # ("SPAN", (4, 9), (5, 9)),
                            # ("SPAN", (1, 10), (2, 10)),
                            # ("SPAN", (4, 10), (5, 10)),
                            # ("SPAN", (1, 11), (2, 11)),
                            # ("SPAN", (4, 11), (5, 11)),
                            # ("SPAN", (1, 12), (2, 12)),
                            # ("SPAN", (4, 12), (5, 12)),
                            # ("SPAN", (0, 13), (-1, 13)),
                            # ("SPAN", (0, 15), (-1, 15)),
                            # ("SPAN", (0, -1), (-1, -1)),
                            ]
    merged_cells = SPAN_SPAN_SPAN_SPAN_

    table = Table(data)
    table.setStyle(TableStyle([
        *merged_cells,
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-2, -2), "CENTER"),
        ("ALIGN", (-1, -1), (-1, -1), "TA_LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Yahei"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 将表格绘制在指定位置
    table.wrapOn(pdf_file, 0, 0)
    table.drawOn(pdf_file, 28, 10)
    # 保存并关闭 PDF 文件
    pdf_file.save()

    return


if __name__ == '__main__':
    result = {
        'sleep_plot': r'E:\\dataset\\x7_data_by_days\\analysis\\20230713\\19921305607_20230713_00_41_35_20230713_08_52_13\\sleep_fig.png',
        'phone_number': '19921305607', 'record_date': '2023-07-13', 'record_start_time': '2023-07-13 00:41:35',
        'record_end_time': '2023-07-13 08:52:13', 'package_loss_rate': '0.27%', 'disconnection_rate': '0.00%',
        'trt': 29475, 'tst': 26805.0, 'sl': 2535, 'waso': 0, 'ar': 0, 'se': '0.91%', 'N1/N2': 235.25, 'N3': 65.0,
        'REM': 146.5}
    save_path = r'E:\dataset\x7_data_by_days\analysis\20230713'

    report_pdf_generator(save_path, result)
