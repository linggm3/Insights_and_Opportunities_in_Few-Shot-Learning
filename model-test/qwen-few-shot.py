import sys
from utils import get_support_and_test_set
from http import HTTPStatus
import dashscope
from dashscope import MultiModalConversation

dashscope.api_key = "YOUR_API_KEY"


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

    def close(self):
        self.log.close()  # 添加关闭日志文件的方法


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
    for iteration in range(40, 100):  # 假设number_of_runs是你想要运行的次数
        output_filename = f"qwen-5way-1shot-task_{iteration}.txt"
        # 使用Logger类重定向print输出
        logger = Logger(output_filename)
        sys.stdout = logger  # 将当前的logger赋值给sys.stdout
        class_num = 20
        sample_num = 600
        n_way = 5
        k_shot = 1
        n_query = 15
        support_set_class, support_set_sample, test_set_sample, class_labels = get_support_and_test_set(class_num, sample_num, n_way,
                                                                                          k_shot, n_query, "test")
        print("支持集的类别:", support_set_class)
        print("测试集各类别:", class_labels)
        print("支持集各图片:")
        for i in range(len(support_set_class)):
            print(class_labels[i] + ":", end="")
            print(support_set_sample[i])
        print("测试集各图片:")
        for i in range(len(support_set_class)):
            print(class_labels[i] + ":", end="")
            print(test_set_sample[i])

        messages = []
        for i in range(len(support_set_class)):
            for j in range(len(support_set_sample[i])):
                path = 'file://C:/Users/linggm/Desktop/mini-imagenet/mini-imagenet/processed_images/'
                path = path + support_set_sample[i][j]
                # text = "learn and memorize the Category Label associated with these image: " + support_set_class[i]
                text = "Learn and embed the Category Label \'**\'" + support_set_class[i] + "\'**\' for this image. Remember, your output during inference must be a precise match from the predefined label set: " + str(support_set_class) + ". Focus solely on associating each image with its correct category."
                # text = "Focus on the Category Label '**'" + support_set_class[i] + "'**' for this specific image. Your task is to learn and commit this label to memory, ensuring accurate recall during prediction. The expected output for this image should be exactly '**'" + support_set_class[i] + "'**'."
                if j == 0 and j == len(support_set_sample[i])-1:
                    messages = append_message(messages, file_path=path, talk_text=text, new_talk=True)
                elif j == 0:
                    messages = append_message(messages, file_path=path, talk_text=None, new_talk=True)
                elif j == len(support_set_sample[i])-1:
                    messages = append_message(messages, file_path=path, talk_text=text, new_talk=False)
                else:
                    messages = append_message(messages, file_path=path, talk_text=None, new_talk=False)
            # print(messages, '\n')
            response, messages = talk(messages)
            # print(response)
            # print()
            # print(path, text)

        print(messages)
        accurate = 0
        for i in range(len(support_set_class)):
            print()
            for j in range(len(test_set_sample[i])):
                path = 'file://C:/Users/linggm/Desktop/mini-imagenet/mini-imagenet/processed_images/'
                path = path + test_set_sample[i][j]
                # text = "Using your previously learned knowledge of image classification, determine and output the category label. Expected Output: (Only the image's category label). Your output should be one of the elements in the list: " + str(support_set_class)
                # text = "Utilizing your previously learned expertise in image classification, identify and present the category label for the image at hand. The expected output should strictly be one of the category labels within this set: " + str(support_set_class) + ". Kindly ensure that your output consists solely of the image's category label."
                # text = "Drawing upon your accumulated knowledge in image classification, accurately discern and provide the specific category label for the given image. It is imperative to note that your output must exclusively be one of the predefined category labels from the list: ' + str(support_set_class) + '. Any response not included in this set will be deemed invalid. Please strictly confine your output to one of the listed category labels only."
                # text1 = str(support_set_class)
                # text2 = "chose a category label form the above list for the image. Expected output: (only the category of the image)"
                # text = text1 + text2
                text1 = "From the previously learned category labels: " + str(support_set_class)
                text2 = ", choose the accurate category label that represents the given image. Expected output: (the single category label of the image)."
                text = text1 + text2
                messages = append_message(messages, path, text, new_talk=True)
                response, messages = talk(messages, is_append=False)
                print(test_set_sample[i][j], end=",")
                print("label=" + support_set_class[i], end=",")
                print("output=" + response.output.choices[0].message.content[0]["text"], end=",")
                # print(messages)
                if correct(response.output.choices[0].message.content[0]["text"], support_set_class[i]):
                    accurate += 1
                    print("True")
                else:
                    print("False")

        print()
        print("acc: ", accurate / (n_way * n_query))
        # 在此之后关闭当前的日志文件
        sys.stdout.close()
        sys.stdout = sys.__stdout__  # 重置sys.stdout为原始标准输出

