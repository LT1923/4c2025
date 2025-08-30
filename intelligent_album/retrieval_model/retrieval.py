import os
import numpy as np
import torch
import faiss
from transformers import AutoTokenizer, AutoModel
import matplotlib
from datetime import datetime

matplotlib.use("Agg")  # 根据环境选择后端
import matplotlib.pyplot as plt
import cv2
import time
import textwrap


class RetrievalModel:
    def __init__(self,
                 model_path=os.path.join(os.path.dirname(__file__), "utils", "my_saved_model"),
                 quantized=True,
                 use_bitblas=False,
                 max_token_length=77,
                 device=None):
        """
        初始化检索模型，包括加载预训练模型、tokenizer、以及相关路径参数
        不加载或构建 embeddings、paths、index 及 annotations。
        """
        if not quantized:
            # model_path = "BAAI/BGE-VL-base"
            model_path = os.path.join(os.path.dirname(__file__), "utils", "hf_models", "BGE-VL-base")
        self.model_path = model_path

        self.photo_root = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                       "uploads")  # 图片路径的根目录, 目前是/root/autodl-tmp/intelligent_album/uploads
        # faiss相关依赖的根目录。每个依赖目前具体在self.faiss_depend_root/utils/faiss_dependencies/[user_id]
        self.faiss_depend_root = os.path.join(os.path.dirname(__file__), "utils", "faiss_dependencies")
        # print(self.faiss_depend_root)  # 在服务器输出'/root/autodl-tmp/intelligent_album/retrieval_model/utils/faiss_dependencies'

        self.max_token_length = max_token_length

        # 设置设备
        self.device = device if device is not None else (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))

        # 加载模型和 tokenizer
        self.model = AutoModel.from_pretrained(self.model_path, trust_remote_code=True).to(self.device)

        # bitblas加速
        self.use_bitblas = use_bitblas
        if quantized:
            if self.use_bitblas:
                from retrieval_model.utils.BitBlasModules import replace_linear2bitblas
                replace_linear2bitblas(self.model)
            else:
                from retrieval_model.utils.TnModules import replace_linear
                replace_linear(self.model)
        self.model.set_processor(self.model_path)
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)

        # 初始化annotations, features,image_paths和index. 都是空字典。键是user_id，值是相应utils
        self.annotations = {}
        self.features = {}
        self.image_paths = {}
        self.index = {}
        '''
        # 加载 annotations（如果文件存在），否则初始化空字典
        if os.path.exists(self.annotations_file):
            self.annotations = self.load_annotations(self.annotations_file)
        else:
            self.annotations = {}
            # 创建annotations
            with open(self.annotations_file, "w") as file:
                pass  # 创建文件，不写入任何内容
        '''

        '''
        if os.path.exists(self.embeddings_file) and os.path.exists(self.paths_file) and os.path.exists(self.index_file):
            print("Loading saved index and embeddings...")

            self.features = np.load(self.embeddings_file)

            with open(self.paths_file, "r") as f:
                self.image_paths = [line.strip() for line in f.readlines()]

            self.index = faiss.read_index(self.index_file)

        else:
            print("Computing embeddings from image_dir...")
            features_list = []
            self.image_paths = []
            # 遍历 image_dir 中的所有图片文件
            for filename in os.listdir(self.image_dir):
                if filename.lower().endswith((".jpg", ".png", ".jpeg", ".bmp")):
                    image_path = os.path.join(self.image_dir, filename)
                    text_description = self.annotations.get(filename, "")
                    print(f"Processing {image_path} with text: {text_description}")
                    feature = self.extract_embedding(image_path=image_path, text=text_description)
                    if feature is not None:
                        features_list.append(feature)
                        self.image_paths.append(image_path)
            if features_list:
                self.features = np.array(features_list, dtype=np.float32)
            else:
                # 假设特征维度为 512
                self.features = np.empty((0, 512), dtype=np.float32)
            np.save(self.embeddings_file, self.features)
            with open(self.paths_file, "w") as f:
                for path in self.image_paths:
                    f.write(path + "\n")
            print("Building HNSW index...")
            self.index = self.build_hnsw_index(self.features)
            faiss.write_index(self.index, self.index_file)
            print("Successfullt built HNSW index")
        '''

    def count_tokens(self, text):
        """计算文本的 token 数量"""
        return len(self.tokenizer.tokenize(text))

    def load_annotations(self, annotation_file):
        """
        解析注释文件，选择合适长度的文本描述。
        在智能相册的实现中，大概率没有文本描述，
        param:
            - annotation_file: 注释文件
        return:
            - annotations: 注释字典
        """
        annotations = {}
        image_texts = {}
        with open(annotation_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("#")
                if len(parts) < 2:
                    continue
                image_name, idx_text = parts[0], parts[1]
                split_result = idx_text.split(" ", 1)
                if len(split_result) == 2:
                    idx, text = split_result
                else:
                    idx = idx_text  # 文本内容为空
                    text = ""
                if image_name not in image_texts:
                    image_texts[image_name] = []
                image_texts[image_name].append(text)
        # 选择合适文本
        for image_name, texts in image_texts.items():
            selected_text = None
            for text in texts:
                if self.count_tokens(text) <= self.max_token_length:
                    selected_text = text
                    break
            if selected_text is None:
                selected_text = self.tokenizer.convert_tokens_to_string(
                    self.tokenizer.tokenize(texts[0])[:self.max_token_length]
                )
            annotations[image_name] = selected_text
        return annotations

    def extract_embedding(self, image_path=None, text=None):
        """提取单个文本、图片或混合输入的 embedding"""
        with torch.no_grad():
            try:
                feature = self.model.encode(images=image_path, text=text)
            except Exception as e:
                print(f"Error in model.encode: {e}")
                feature = None
        if feature is None:
            return None
        return feature.cpu().numpy().astype(np.float32).flatten()

    def build_hnsw_index(self, features, ef_construction=200, ef_search=50, M=16):
        """使用 FAISS 构建 HNSW 索引"""
        dim = features.shape[1]
        index = faiss.IndexHNSWFlat(dim, M)
        index.hnsw.efConstruction = ef_construction
        index.hnsw.efSearch = ef_search
        index.add(features)
        return index

    def visualize_results(self, user_id, query_image, query_text, results, annotations, k=5):
        """
        使用 Matplotlib 可视化查询结果，并在图片下方显示对应的标注
        存储在~/retrieval_model/retrieval_results下
        """
        if results is None:
            print("results is None")
            return None

        save_path = os.path.join(os.path.dirname(__file__), "retrieval_results", f"{user_id}")
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        plt.figure(figsize=(12, 6))

        def wrap_text(text, width=30):
            return "\n".join(textwrap.wrap(text, width))

        # 显示查询图片
        if query_image:
            img = cv2.imread(query_image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            plt.subplot(2, k, 1)
            plt.imshow(img)
            plt.axis("off")
            plt.title("Query Image")
        # 显示查询文本
        plt.subplot(2, k, k // 2 + 1)
        plt.text(0.5, 0.5, wrap_text(query_text), fontsize=12, ha="center", va="center")
        plt.axis("off")
        # 显示 Top-K 结果
        for i, (img_path, caption, score) in enumerate(results[:k]):
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            plt.subplot(2, k, k + i + 1)
            plt.imshow(img)
            plt.axis("off")
            wrapped_caption = wrap_text(caption, width=30)
            plt.title(f"Rank {i + 1}\n{score:.4f}\n{wrapped_caption}")
        plt.tight_layout()

        # 用当前时间给本次检索结果起名
        current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        result_file_name = f"result_{current_time}.jpg"
        save_path = os.path.join(save_path, result_file_name)

        plt.savefig(save_path)
        plt.show()

    def search(self, user_id, query_feature, k=5):
        """
        在索引中搜索最近的 k 个邻居，返回 (image_path, caption, distance) 列表
        使用类中已加载的 self.index, self.image_paths 及 self.annotations
        """
        self.check_dependencies(user_id)

        if query_feature is None:
            print("query_feature is None")
            return None
        query_feature = query_feature.reshape(1, -1)
        D, I = self.index[user_id].search(query_feature, k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx == -1:
                break
            print(dist, idx)
            image_path = self.image_paths[user_id][idx]
            caption = self.annotations[user_id].get(image_path, "No annotation")
            results.append((image_path, caption, dist))
        return results

    def query(self, user_id, text_input=None, image_address=None, top_k=5):
        """
        搜索api
        执行查询：
          1. 使用类中保存的 annotations、embeddings、paths、index
          2. 对输入进行混合查询，并可视化结果
        返回： (query_text, query_image, results)
        """
        self.check_dependencies(user_id)

        start_time = time.time()
        query_text = text_input
        query_image = image_address
        # 获取输入的特征
        query_feature = self.extract_embedding(image_path=query_image, text=query_text)

        if query_feature is None:
            print("query_feature is None")
            return None

        # 根据特征检索
        results = self.search(user_id, query_feature, k=top_k)
        # self.visualize_results(user_id, query_image, query_text, results, annotations=self.annotations[user_id],k=top_k)
        end_time = time.time()
        print(f"time: {end_time - start_time:.2f}s")
        print(results)
        # return query_text, query_image, results
        return results

    def add_image(self, user_id, new_image_path, caption_text=""):
        """
        增加图片api
        接收user_id参数，根据user_id确定操作路径和faiss依赖
        将用户输入的图片和文本标注添加到目标文件夹和注释文件中，
        同时更新 self.annotations、self.features、self.image_paths 和 self.index，
        避免每次都重新加载。
        新图片文件来自参数，都是路径。
        返回更新后的 (features, image_paths)
        param:
            - user_id: 用户id
            - new_image_path: 新增图片的路径（格式为~/uploads/user_id/xxx.jpg）,详见photo_routes.py中upload_photo函数
            - caption_text: 图片注释。大概率没有，因为用户不会输入这个……
        """
        # 确保各个依赖变量已经正常初始化
        self.check_dependencies(user_id)

        faiss_depend_dir = os.path.join(self.faiss_depend_root, f"{user_id}")
        index_file = os.path.join(faiss_depend_dir, "faiss_index.faiss")
        embeddings_file = os.path.join(faiss_depend_dir, "bgevl_embeddings.npy")
        paths_file = os.path.join(faiss_depend_dir, "bgevl_image_paths.txt")
        annotations_file = os.path.join(faiss_depend_dir, "annotations.txt")

        # 这些工作photo_routes.py已经干了
        '''
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        根据 target_dir 中已有 .jpg 文件数量生成新图片名称
        existing_images = [f for f in os.listdir(target_dir) if f.endswith(".jpg")]
        existing_numbers = [int(f.split(".")[0]) for f in existing_images if f.split(".")[0].isdigit()]
        next_image_number = max(existing_numbers) + 1 if existing_numbers else 1
        new_image_name = f"{next_image_number}.jpg"
        target_image_path = os.path.join(target_dir, new_image_name)  # 为新添加的图片的设置的路径

        try:
            shutil.copy(new_image, target_image_path)
            print(f"图片已复制到 {target_image_path}")
        except Exception as e:
            print(f"复制图片时出错: {e}")
            return None, None
        '''
        # 写入新的标注（格式：文件名#0 标注）
        # 不从文件名构建caption_text
        # caption_text = os.path.splitext(os.path.basename(new_image_path))[0]
        annotation_line = f"{new_image_path}#0 {caption_text}\n"
        try:
            with open(annotations_file, "a", encoding="utf-8") as f:
                f.write(annotation_line)
            print("注释已添加。")
        except Exception as e:
            print(f"写入注释文件时出错: {e}")
            return None, None

        # 更新 self.annotations（字典映射文件名到标注）
        self.annotations[user_id][new_image_path] = caption_text
        print(f"annotations for {user_id}: ", len(self.annotations[user_id]))

        # 更新 self.image_paths
        self.image_paths[user_id].append(new_image_path)

        # 提取新图片的特征向量
        new_feature = self.extract_embedding(image_path=new_image_path, text=caption_text)
        if new_feature is None:
            print("提取特征失败")
            return None, None
        new_feature = new_feature.reshape(1, -1)

        # 如果维度不匹配，则报错（确保之前构建时使用的维度一致）
        if self.features[user_id].size > 0 and self.features[user_id].shape[1] != new_feature.shape[1]:
            print(
                f"维度不匹配: self.features[{user_id}].shape = {self.features[user_id].shape}, new_feature.shape = {new_feature.shape}")
            return None, None

        # 更新 self.features
        if self.features[user_id].size == 0:
            self.features[user_id] = new_feature
        else:
            self.features[user_id] = np.vstack([self.features[user_id], new_feature])

        print(f"features for {user_id}: ", self.features[user_id])

        # 更新 FAISS 索引
        self.index[user_id].add(new_feature)
        faiss.write_index(self.index[user_id], index_file)
        print(f"index for {user_id}: ", self.index[user_id])

        # 更新磁盘文件
        np.save(embeddings_file, self.features[user_id])
        with open(paths_file, "w") as f:
            for path in self.image_paths[user_id]:
                f.write(path + "\n")
        print(f"paths for {user_id}: ", len(self.image_paths[user_id]))

        print("新图片及标注已成功添加。")
        return self.features[user_id], self.image_paths[user_id]

    def delete_image(self, user_id, image_path):
        """
        删除图片api
        删除指定 image_path 对应的图片文件及其相关信息：
         - 从 self.image_paths 中删除该路径
         - 从 self.features 中删除对应的特征向量行
         - 从 self.annotations 字典中删除对应条目
         - 重建 FAISS 索引并更新磁盘文件：embeddings_file、paths_file 和 annotations_file
        参数：
            user_id: 用户id
            image_path: 要删除的图片文件的绝对路径
        返回 True 表示成功，否则返回 False
        """
        # 确保各个依赖变量已经正常初始化
        self.check_dependencies(user_id)

        faiss_depend_dir = os.path.join(self.faiss_depend_root, f"{user_id}")
        index_file = os.path.join(faiss_depend_dir, "faiss_index.faiss")
        embeddings_file = os.path.join(faiss_depend_dir, "bgevl_embeddings.npy")
        paths_file = os.path.join(faiss_depend_dir, "bgevl_image_paths.txt")
        annotations_file = os.path.join(faiss_depend_dir, "annotations.txt")
        # 在 self.image_paths 中找到对应的索引
        idx = None
        for i, path in enumerate(self.image_paths[user_id]):
            if path == image_path:
                idx = i
                break
        if idx is None:
            print(f"图片 {image_path} 不存在于系统中。")
            return False

        # 删除磁盘上的图片文件（可选）-- 这个工作photo_routes_model.py已经干了
        '''
        try:
            os.remove(self.image_paths[user_id][idx])
            print(f"已删除磁盘中的文件 {self.image_paths[user_id][idx]}")
        except Exception as e:
            print(f"删除磁盘文件时出错: {e}")
        '''

        # 删除对应的特征向量行
        print(f"before delete, features for {user_id}: ", self.features[user_id])
        self.features[user_id] = np.delete(self.features[user_id], idx, axis=0)
        print(f"after delete, features for {user_id}: ", self.features[user_id])
        # 删除对应的路径
        print(f"before delete, paths for {user_id}: ", len(self.image_paths[user_id]))
        del self.image_paths[user_id][idx]
        print(f"after delete, paths for {user_id}: ", len(self.image_paths[user_id]))

        # 删除 self.annotations 中对应的条目
        print(f"before delete, annotations for {user_id}: ", len(self.annotations[user_id]))
        if image_path in self.annotations[user_id]:
            del self.annotations[user_id][image_path]
        print(f"after delete, annotations for {user_id}: ", len(self.annotations[user_id]))

        # 重新构建 FAISS 索引（如果剩余特征不为空，否则创建空索引）
        print(f"before delete, index for {user_id}: ", self.index[user_id])
        if self.features[user_id].shape[0] > 0:
            self.index[user_id] = self.build_hnsw_index(self.features[user_id])
        else:
            dim = self.features[user_id].shape[1] if self.features[user_id].size > 0 else 512
            self.index[user_id] = faiss.IndexHNSWFlat(dim, 32)
        faiss.write_index(self.index[user_id], index_file)
        print(f"after delete, index for {user_id}: ", self.index[user_id])

        # 更新磁盘文件：embeddings_file 和 paths_file
        np.save(embeddings_file, self.features[user_id])
        with open(paths_file, "w") as f:
            for path in self.image_paths[user_id]:
                f.write(path + "\n")

        # 更新 annotations_file（重写所有条目）
        with open(annotations_file, "w", encoding="utf-8") as f:
            for file_path, annotation in self.annotations[user_id].items():
                f.write(f"{file_path}#0 {annotation}\n")

        print(f"图片 {image_path} 已被删除，并更新所有相关文件。")
        return True

    def get_all_image_annotation_pairs(self, user_id):
        """返回一个包含所有 (图片地址, 标注信息) 的列表"""
        self.check_dependencies(user_id)
        return [(image_path, self.annotations[user_id].get(image_path, "No annotation"))
                for image_path in self.image_paths[user_id]]

    def check_dependencies(self, user_id):
        """
        检查各个依赖变量是否初始化
        """
        print("--------------check dependencies---------------")
        # 检查相册路径
        target_dir = os.path.join(self.photo_root, f"{user_id}")  # 根据user_id确定目标路径
        os.makedirs(target_dir, exist_ok=True)

        # 检查依赖路径
        faiss_depend_dir = os.path.join(self.faiss_depend_root, f"{user_id}")
        os.makedirs(faiss_depend_dir, exist_ok=True)
        index_file = os.path.join(faiss_depend_dir, "faiss_index.faiss")
        embeddings_file = os.path.join(faiss_depend_dir, "bgevl_embeddings.npy")
        paths_file = os.path.join(faiss_depend_dir, "bgevl_image_paths.txt")
        annotations_file = os.path.join(faiss_depend_dir, "annotations.txt")

        if os.path.exists(annotations_file):
            self.annotations[user_id] = self.load_annotations(annotations_file)
        if self.annotations.get(user_id) is None:
            self.annotations[user_id] = {}
            if not os.path.exists(annotations_file):
                with open(annotations_file, "w") as file:
                    pass

        # 加载 embeddings, image_paths 和 index（如果文件存在），否则从 image_dir 构建
        if os.path.exists(embeddings_file) and os.path.exists(paths_file) and os.path.exists(index_file):
            print("Loading saved index and embeddings...")
            self.features[user_id] = np.load(embeddings_file)

            with open(paths_file, "r") as f:
                self.image_paths[user_id] = [line.strip() for line in f.readlines()]

            self.index[user_id] = faiss.read_index(index_file)
        else:
            self.features[user_id] = np.empty((0, 512), dtype=np.float32)
            np.save(embeddings_file, self.features[user_id])

            self.image_paths[user_id] = []
            with open(paths_file, "w") as f:
                for path in self.image_paths[user_id]:
                    f.write(path + "\n")

            self.index[user_id] = self.build_hnsw_index(self.features[user_id])
            faiss.write_index(self.index[user_id], index_file)
            '''
            features_list = []
            self.image_paths[user_id] = []
            for filename in os.listdir(target_dir):
                if filename.lower().endswith((".jpg", ".png", ".jpeg", ".bmp")):
                    image_path = os.path.join(target_dir, filename)
                    self.image_paths[user_id].append(image_path)
                    text_description = self.annotations[user_id].get(image_path, "")
                    print(f"Processing {image_path} with text: {text_description}")
                    feature = self.extract_embedding(image_path=image_path, text=text_description)
                    if feature is not None:
                        features_list.append(feature)
            if features_list:
                self.features[user_id] = np.array(features_list, dtype=np.float32)
            else:
                # 假设特征维度为 512
                self.features[user_id] = np.empty((0, 512), dtype=np.float32)
            np.save(embeddings_file, self.features[user_id])
            with open(paths_file, "w") as f:
                for path in self.image_paths[user_id]:
                    f.write(path + "\n")
            print("Building HNSW index...")
            self.index[user_id] = self.build_hnsw_index(self.features[user_id])
            faiss.write_index(self.index[user_id], index_file)
            '''
        print(f"annotations for {user_id}: ", len(self.annotations[user_id]))
        print(f"index for {user_id}: ", self.index[user_id])
        print(f"paths for {user_id}: ", len(self.image_paths[user_id]))
        print(f"features for {user_id}: ", self.features[user_id])


if __name__ == "__main__":
    # 模拟photo_routes_model.py中对RetrievalModel的调用
    # 注意：此处执行的删除和添加操作并不会在物理上删除或添加实际文件夹的文件，只会通过修改annotation和faiss依赖来反映
    # 只有在photo_routes_model.py中的增删才会在物理上增删实际文件夹中的文件。todo: 测试photo_routes_model.py
    print("initialize the model!")
    retrieval_model = RetrievalModel(
        quantized=False,
        use_bitblas=False
    )
    #retrieval_model.query(2,text_input="dog",image_address="/home/ecs-assist-user/album/intelligent_album/uploads/2")

    # print(retrieval_model.get_all_image_annotation_pairs(user_id=1))
    #
    # # 删除图片
    # print("delete image!")
    # retrieval_model.delete_image(1, "/root/autodl-tmp/intelligent_album/uploads/1/boat.jpg")
    # print(retrieval_model.get_all_image_annotation_pairs(user_id=1))
    #
    # # 重新添加图片
    # print("add image again!")
    # retrieval_model.add_image(1, "/root/autodl-tmp/intelligent_album/uploads/1/boat.jpg")
    # print(retrieval_model.get_all_image_annotation_pairs(user_id=1))

    # 查询图片
    # print("search image with text: boat!")
    # retrieval_model.query(
    #     user_id=1,
    #     text_input="boat"
    # )
    #
    # print("search image with text: plane!")
    # retrieval_model.query(
    #     user_id=1,
    #     text_input="plane"
    # )
    #
    # print("search image with text: sun!")
    # retrieval_model.query(
    #     user_id=1,
    #     text_input="sun"
    # )
    #
    # print("search image with text: football!")
    # retrieval_model.query(
    #     user_id=1,
    #     text_input="football"
    # )

    print("search image with text: tree!")
    retrieval_model.query(
        user_id=1,
        text_input="boat and lake"
    )
