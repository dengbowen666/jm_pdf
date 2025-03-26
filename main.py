import jmcomic
import os
import time
import yaml
import argparse
from PIL import Image
def all2PDF(input_folder, pdfpath, pdfname):
    start_time = time.time()
    paht = input_folder
    zimulu = []  # 子目录（里面为image）
    image = []  # 子目录图集
    sources = []  # pdf格式的图

    with os.scandir(paht) as entries:
        for entry in entries:
            if entry.is_dir():
                zimulu.append(int(entry.name))
    # 对数字进行排序
    zimulu.sort()

    for i in zimulu:
        with os.scandir(paht + "/" + str(i)) as entries:
            for entry in entries:
                if entry.is_dir():
                    print("这一级不应该有自录")
                if entry.is_file():
                    image.append(paht + "/" + str(i) + "/" + entry.name)

    if "jpg" in image[0]:
        output = Image.open(image[0])
        image.pop(0)

    for file in image:
        if "jpg" in file:
            img_file = Image.open(file)
            if img_file.mode == "RGB":
                img_file = img_file.convert("RGB")
            sources.append(img_file)

    pdf_file_path = pdfpath + "/" + pdfname
    if pdf_file_path.endswith(".pdf") == False:
        pdf_file_path = pdf_file_path + ".pdf"
    output.save(pdf_file_path, "pdf", save_all=True, append_images=sources)
    end_time = time.time()
    run_time = end_time - start_time
    print("运行时间：%3.2f 秒" % run_time)


if __name__ == "__main__":
    # 配置参数解析
    parser = argparse.ArgumentParser(description='JM漫画下载转换工具')
    parser.add_argument('ids', nargs='+', type=str,
                        help='要下载的漫画ID（支持多个，用空格分隔）')
    parser.add_argument('--config', default="E:/学习/大佬作品/image2pdf/config.yml",
                        help='配置文件路径（默认：config.yml）')
    parser.add_argument('--no-convert', action='store_true',  # ← 保留跳过转换的选项
                        help='禁用PDF转换（默认会自动转换）')  # 修改帮助说明
    args = parser.parse_args()

    # 加载配置
    try:
        loadConfig = jmcomic.JmOption.from_file(args.config)
        with open(args.config, "r", encoding="utf8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            base_path = data["dir_rule"]["base_dir"]
    except Exception as e:
        print(f"配置加载失败: {str(e)}")
        exit(1)

    # 下载漫画
    for comic_id in args.ids:
        print(f"正在下载漫画 {comic_id}...")
        jmcomic.download_album(comic_id, loadConfig)

    # PDF转换（除非设置了--no-convert）
    if not args.no_convert:
        with os.scandir(base_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    pdf_path = os.path.join(base_path, f"{entry.name}.pdf")
                    if os.path.exists(pdf_path):
                        print(f"文件《{entry.name}》已存在，跳过")
                        continue
                    print(f"开始转换：{entry.name}")
                    all2PDF(
                        os.path.join(base_path, entry.name),
                        base_path,
                        entry.name
                    )