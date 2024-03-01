from utils import get_support_and_test_set, get_label_dict
from http import HTTPStatus
import dashscope
import sys
from dashscope import MultiModalConversation

dashscope.api_key = "sk-49cc848c6be942d3b0ff21bc165e1be4"


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
        talk_messages[-1]['content'].append({'image': file_path})
    if talk_text:
        talk_messages[-1]['content'].append({'text': talk_text})
    return talk_messages


def talk(talk_messages=[], is_append=True):
    response = MultiModalConversation.call(model='qwen-vl-plus', messages=talk_messages)
    if is_append:
        talk_messages.append({'role': response.output.choices[0].message.role,
                              'content': response.output.choices[0].message.content})
    else:
        talk_messages.pop(-1)

    return response, talk_messages


if __name__ == "__main__":
    # 使用Logger类重定向print输出
    sys.stdout = Logger('output.txt')
    class_num = 20
    sample_num = 600
    n_way = 20
    k_shot = 0
    n_query = 100
    support_set_class, support_set_sample, test_set_sample, class_labels = \
        get_support_and_test_set(class_num, sample_num, n_way, k_shot, n_query, "test")
    print("测试集20个类别，每个类别10张图片")
    print("测试集各类别:", support_set_class)
    print("测试集各类别:", class_labels)
    for i in range(len(support_set_class)):
        print(class_labels[i] + ":", end="")
        print(test_set_sample[i])
    # print("测试集各图片:", test_set_sample)
    dict_path = r"C:\Users\linggm\Desktop\mini-imagenet\map.txt"
    # 读取标签映射文件
    label_dict = get_label_dict(dict_path)
    text1 = "['hourglass', 'lion', 'bookshop', 'crate', 'mixing_bowl', 'dalmatian', 'cuirass', 'black-footed_ferret', 'theater_curtain', 'school_bus', 'vase', 'trifle', 'malamute', 'ant', 'golden_retriever', 'scoreboard', 'king_crab', 'African_hunting_dog', 'nematode', 'electric_guitar']"
    # text1 = "['hourglass', 'lion', 'bookshop', 'crate', 'mixing_bowl', 'dalmatian', 'cuirass', 'black-footed_ferret', 'theater_curtain', 'school_bus', 'vase', 'trifle', 'malamute', 'ant', 'golden_retriever', 'scoreboard', 'king_crab', 'African_hunting_dog', 'nematode', 'electric_guitar', 'Walker_hound', 'boxer', 'dishrag', 'spider_web', 'Arctic_fox', 'chime', 'parallel_bars', 'organ', 'barrel', 'solar_dish', 'French_bulldog', 'fire_screen', 'komondor', 'Newfoundland', 'worm_fence', 'slot', 'file', 'consomme', 'Tibetan_mastiff', 'jellyfish', 'lipstick', 'snorkel', 'triceratops', 'pencil_box', 'carousel', 'photocopier', 'reel', 'house_finch', 'harvestman', 'tank', 'bolete', 'cliff', 'prayer_rug', 'three-toed_sloth', 'tobacco_shop', 'yawl', 'rock_beauty', 'Gordon_setter', 'dugong', 'dome', 'frying_pan', 'green_mamba', 'hotdog', 'Saluki', 'toucan', 'oboe', 'aircraft_carrier', 'unicycle', 'stage', 'cocktail_shaker', 'street_sign', 'miniature_poodle', 'holster', 'beer_bottle', 'robin', 'ladybug', 'wok', 'hair_slide', 'tile_roof', 'upright', 'orange', 'ear', 'clog', 'ashcan', 'white_wolf', 'combination_lock', 'goose', 'Ibizan_hound', 'poncho', 'iPod', 'cannon', 'miniskirt', 'coral_reef', 'horizontal_bar', 'catamaran', 'rhinoceros_beetle', 'carton', 'meerkat', 'garbage_truck', 'missile']"

    messages = []

    accurate = 0
    for i in range(len(support_set_class)):
        print()
        for j in range(len(test_set_sample[i])):
            path = 'file://C:/Users/linggm/Desktop/mini-imagenet/mini-imagenet/processed_images/'
            path = path + test_set_sample[i][j]
            text = "chose a category label form the above list for the image. Expected output: (only the category of the image)"
            messages = append_message(messages, None, text1, new_talk=True)
            messages = append_message(messages, path, text, new_talk=False)
            # print(messages)
            response, messages = talk(messages, is_append=False)
            print(test_set_sample[i][j], end=",")
            print("label=" + support_set_class[i], end=",")
            print("output=" + response.output.choices[0].message.content[0]["text"], end=",")
            # print(response)
            # print(messages)
            if correct(response.output.choices[0].message.content[0]["text"], support_set_class[i]):
                accurate += 1
                print("True")
            else:
                print("False")

    print()
    print("acc: ", accurate / (n_way * n_query))
