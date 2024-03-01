import ast
import csv
import random


def generate_random_lists(a, b, n, k1, k2):
    """
        生成两个列表：
        1. 从1到a中随机选择n个整数的n维列表。
        2. 对于每个选出的整数，首先从1到b中随机选择k个整数，
           然后将这k个整数分割成两个不相交的子集，形成一个n*k1维列表和一个n*k2维列表。

        :param a: 选择整数的上限a
        :param b: 选择整数的上限b
        :param n: 从0到a-1中选择的整数个数
        :param k: 对于每个从0到a-1中选择的整数，初始从1到b-1中选择的整数个数
        :param k1: 每个整数子集中分配给result_nk1的整数个数
        :param k2: 每个整数子集中分配给result_nk2的整数个数（必须满足k1 + k2 == k）
        :return: 两个列表，第一个是n*k1维的，第二个是n*k2维的
    """
    k = k1 + k2  # k1与k2之和必须等于k

    # 从1到a中随机选择n个整数
    selected_n = random.sample(range(0, a), n)

    # 初始化n*k1维和n*k2维结果列表
    result_nk1 = []
    result_nk2 = []

    # 对于每个选出的n个整数，先从1到b中随机选择k个整数，然后分割为两部分
    for num in selected_n:
        selected_k = random.sample(range(0, b), k)

        # 确保k1和k2不相交地分割选定的k个整数
        selected_k1 = random.sample(selected_k, k1)
        selected_k2 = random.sample(set(selected_k) - set(selected_k1), k2)

        result_nk1.append(selected_k1)
        result_nk2.append(selected_k2)

    return selected_n, result_nk1, result_nk2


# 读取txt，做label的映射
def get_label_dict(path):
    file = open(path)
    text_content = file.read()

    # 使用Python字典推导式，将文本内容转换为所需格式的字典
    # 首先使用ast.literal_eval将字符串转换为字典
    initial_dict = ast.literal_eval(f"{{{text_content}}}")

    # 然后将这个字典的每个项转换为新的键值对，其中键是原字典值的第一个元素，值是第二个元素
    corrected_dict = {value[0]: value[1] for value in initial_dict.values()}

    # 打印转换后的字典
    # print(corrected_dict)
    return corrected_dict


def read_csv(path):
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
    rows.pop(0)
    # print(len(rows))
    return rows


def get_img_name(set_class, set_sample, csv_file, dict_file):
    set_class_label = []
    set_class_label_name = []
    set_sample_name = []
    # 对每个类别
    for idx, i in enumerate(set_class):
        # 得到类别的名字
        class_label = csv_file[600 * i][1]
        set_class_label.append(class_label)
        set_class_label_name.append(dict_file[class_label])
        # 得到每个样本点对应的图片名
        sample_name = []
        for j in set_sample[idx]:
            img_name = csv_file[600 * i + j][0]
            sample_name.append(img_name)
        set_sample_name.append(sample_name)
    return set_class_label_name, set_sample_name, set_class_label


def get_support_and_test_set(class_num=20, sample_num=600, n_way=5, k_shot=5, n_query=15, type_="test"):
    # class_num = 20
    # sample_num = 600
    # n_way = 5
    # k_shot = 5
    if type_ == "test":
        csv_path = r"C:\Users\linggm\Desktop\mini-imagenet\test.csv"
    elif type_ == "train":
        csv_path = r"C:\Users\linggm\Desktop\mini-imagenet\train.csv"
    else:
        csv_path = r"C:\Users\linggm\Desktop\mini-imagenet\val.csv"
    dict_path = r"C:\Users\linggm\Desktop\mini-imagenet\map.txt"

    # 读取 test.csv 文件
    label_dict = get_label_dict(dict_path)
    # 读取标签映射文件
    csv_data = read_csv(csv_path)

    # 生成支持集的 n_way 个类别，对每个类别生成 k_shot 个样本点,生成测试用的 n_way * k_shot 个样本
    support_set_class_num, support_set_sample_num, test_set_sample_num = generate_random_lists(class_num, sample_num, n_way, k_shot, n_query)
    # support_set_class_num = [0, 2, 7, 11, 17]
    # _, test_set_sample_num = generate_random_lists(class_num, sample_num, n_way, k_shot)
    # print("支持集的类别:", support_set_class_num)
    # print("支持集各图片:", support_set_sample_num)
    # print("测试集各图片:", test_set_sample_num)

    # 将类别从数字转换为标签字符串，得到样本点对应的图片名
    support_set_class, support_set_sample, support_set_class_label = get_img_name(support_set_class_num, support_set_sample_num, csv_data, label_dict)
    _, test_set_sample, test_set_class_label = get_img_name(support_set_class_num, test_set_sample_num, csv_data, label_dict)
    # print("支持集的类别:", support_set_class)
    # print("支持集各图片:", support_set_sample)
    # print("测试集各图片:", test_set_sample)

    return support_set_class, support_set_sample, test_set_sample, support_set_class_label


if __name__ == "__main__":
    a, b, c, d = get_support_and_test_set(20, 600, 5, 1, 15)