from utils import get_support_and_test_set, get_label_dict
from zhipuai import ZhipuAI
import oss2
import sys
import os
# client = ZhipuAI(api_key="c544b26a002c3ebf6fa1d0c2b4394523.Lm0XC6Py2OHdYHDp")
# client = ZhipuAI(api_key="3014b4448c84ca603bfceedf3865b767.m6eQzxqBRWYnPY5P")
# client = ZhipuAI(api_key="d2e0744382e2d399ca1c2d2e1e555f66.IVZSjor3A0yJsBgF")
# client = ZhipuAI(api_key="f47ff89678ae47ae1753dc89e85249c4.SdL8RHxFnbufL50k")
# client = ZhipuAI(api_key="f381cc728a64341e6b3ab0546f6c463f.xBI7N0FDWfoQJRQT")
# client = ZhipuAI(api_key="8d5cba21014fc03b12c63d05b464cba3.Lrt5k4RXthvubU6g")
client = ZhipuAI(api_key="3014b4448c84ca603bfceedf3865b767.m6eQzxqBRWYnPY5P")

# 阿里云Access Key ID和Access Key Secret
auth = oss2.Auth('LTAI5tM4GcxsGVuwbCMpzZ53', 'fP48uGjF7xmJoo4ZE8bsKzonwJp6LF')

# Bucket名称和数据中心所在的区域
bucket = oss2.Bucket(auth, 'http://oss-cn-guangzhou.aliyuncs.com', 'eggeggegg')


def upload_image(image_path):
    """
    上传图片到OSS并返回URL。

    参数:
    - image_path: 图片的本地路径

    返回:
    - 上传后的图片URL
    """

    # 上传文件到OSS
    object_name = os.path.basename(image_path)  # 将图片文件名作为OSS中的object key
    bucket.put_object_from_file(object_name, image_path)

    # 获取公共读的URL（如果需要公开访问的话）
    public_url = bucket.sign_url('GET', object_name, 1 * 60)  # 签名有效期一小时

    return public_url


class Logger(object):
    def __init__(self, filename="output.txt"):
        self.terminal = sys.stdout  # 原始stdout
        self.log = open(filename, 'w')  # 打开或创建txt文件以追加模式

    def write(self, message):
        self.terminal.write(message)  # 输出到控制台
        self.log.write(message)  # 写入到文件

    def flush(self):
        self.terminal.flush()
        self.log.flush()  # 可能需要刷新缓冲区，确保立即写入文件


def correct(out, label):
    out = out.lower()
    label = label.lower()
    label = label.split("_")
    for item in label:
        if item not in out:
            return False
    return True


def append_message(talk_messages, file_path=None, talk_text=None, new_talk=False):
    if new_talk:
        talk_messages.append({"role": "user",
                              'content': [
                              ]})
    if file_path:
        uploaded_image_url = upload_image(file_path)
        talk_messages[-1]['content'].append({
                        "type": "image_url",
                        "image_url": {
                            "url": uploaded_image_url
                        }
                    })
    if talk_text:
        talk_messages[-1]['content'].append({
                        "type": "text",
                        "text": talk_text
        })
    return talk_messages


def talk(talk_messages=[], is_append=True):
    response = client.chat.completions.create(
        model="glm-4v",
        messages=talk_messages
    )
    if is_append:
        talk_messages.append({'role': response.choices[0].message.role,
                              'content': response.choices[0].message.content})
    else:
        talk_messages.pop(-1)

    return response, talk_messages


# 示例使用
if __name__ == '__main__':
    # 使用Logger类重定向print输出
    sys.stdout = Logger('output.txt')
    class_num = 20
    sample_num = 600
    n_way = 20
    k_shot = 0
    n_query = 100
    support_set_class1, support_set_sample1, test_set_sample1, class_labels1 = \
        get_support_and_test_set(class_num, sample_num, n_way, k_shot, n_query, "test")
    class_num = 64
    sample_num = 600
    n_way = 64
    k_shot = 0
    n_query = 100
    support_set_class2, support_set_sample2, test_set_sample2, class_labels2 = \
        get_support_and_test_set(class_num, sample_num, n_way, k_shot, n_query, "train")
    class_num = 16
    sample_num = 600
    n_way = 16
    k_shot = 0
    n_query = 100
    support_set_class3, support_set_sample3, test_set_sample3, class_labels3 = \
        get_support_and_test_set(class_num, sample_num, n_way, k_shot, n_query, "val")

    # support_set_class = support_set_class1 + support_set_class2 + support_set_class3
    # support_set_sample = support_set_sample1 + support_set_sample2 + support_set_sample3
    # test_set_sample = test_set_sample1 + test_set_sample2 + test_set_sample3
    # class_labels = class_labels1 + class_labels2 + class_labels3
    support_set_class = support_set_class2
    support_set_sample = support_set_sample2
    test_set_sample = test_set_sample2
    class_labels = class_labels2

    print("测试集64个类别，每个类别100张图片")
    print("测试集各类别:", support_set_class)
    print("测试集各类别:", class_labels)
    for i in range(len(support_set_class)):
        print(class_labels[i] + ":", end="")
        print(test_set_sample[i])
    # print("测试集各图片:", test_set_sample)
    dict_path = r"C:\Users\linggm\Desktop\mini-imagenet\map.txt"
    # 读取标签映射文件
    label_dict = get_label_dict(dict_path)
    # text1 = "['hourglass', 'lion', 'bookshop', 'crate', 'mixing_bowl', 'dalmatian', 'cuirass', 'black-footed_ferret', 'theater_curtain', 'school_bus', 'vase', 'trifle', 'malamute', 'ant', 'golden_retriever', 'scoreboard', 'king_crab', 'African_hunting_dog', 'nematode', 'electric_guitar']"
    text1 = "['hourglass', 'lion', 'bookshop', 'crate', 'mixing_bowl', 'dalmatian', 'cuirass', 'black-footed_ferret', 'theater_curtain', 'school_bus', 'vase', 'trifle', 'malamute', 'ant', 'golden_retriever', 'scoreboard', 'king_crab', 'African_hunting_dog', 'nematode', 'electric_guitar', 'Walker_hound', 'boxer', 'dishrag', 'spider_web', 'Arctic_fox', 'chime', 'parallel_bars', 'organ', 'barrel', 'solar_dish', 'French_bulldog', 'fire_screen', 'komondor', 'Newfoundland', 'worm_fence', 'slot', 'file', 'consomme', 'Tibetan_mastiff', 'jellyfish', 'lipstick', 'snorkel', 'triceratops', 'pencil_box', 'carousel', 'photocopier', 'reel', 'house_finch', 'harvestman', 'tank', 'bolete', 'cliff', 'prayer_rug', 'three-toed_sloth', 'tobacco_shop', 'yawl', 'rock_beauty', 'Gordon_setter', 'dugong', 'dome', 'frying_pan', 'green_mamba', 'hotdog', 'Saluki', 'toucan', 'oboe', 'aircraft_carrier', 'unicycle', 'stage', 'cocktail_shaker', 'street_sign', 'miniature_poodle', 'holster', 'beer_bottle', 'robin', 'ladybug', 'wok', 'hair_slide', 'tile_roof', 'upright', 'orange', 'ear', 'clog', 'ashcan', 'white_wolf', 'combination_lock', 'goose', 'Ibizan_hound', 'poncho', 'iPod', 'cannon', 'miniskirt', 'coral_reef', 'horizontal_bar', 'catamaran', 'rhinoceros_beetle', 'carton', 'meerkat', 'garbage_truck', 'missile']"

    messages = []

    accurate = 0
    for i in range(len(support_set_class)):
        print()
        for j in range(len(test_set_sample[i])):
            path = 'C:/Users/linggm/Desktop/mini-imagenet/mini-imagenet/processed_images/'
            path = path + test_set_sample[i][j]
            text = "Classify the image into one of the following predefined categories:" + text1 + "It is crucial that your response contains only the name of the category that accurately describes the image and is included in the provided list. Outputs with categories not found in the list will be considered invalid. Do not include any additional text or explanations."
            # messages = append_message(messages, None, text1, new_talk=True)
            messages = append_message(messages, path, text, new_talk=True)
            # print(messages)
            response, messages = talk(messages, is_append=False)
            # print(response)
            # print()
            # print(messages)
            print(test_set_sample[i][j], end=",")
            print("label=" + support_set_class[i], end=",")
            print("output=" + response.choices[0].message.content, end=",")
            # print(response)
            # print(messages)
            if correct(response.choices[0].message.content, support_set_class[i]):
                accurate += 1
                print("True")
            else:
                print("False")

    print()
    print("acc: ", accurate / (84 * n_query))
