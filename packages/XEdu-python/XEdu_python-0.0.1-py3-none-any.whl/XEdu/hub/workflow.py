from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Type, Union
import cv2
import json
import numpy as np
import warnings
if TYPE_CHECKING:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
import onnxruntime as ort
import time
import io
import matplotlib.pyplot as plt
import pprint
from openxlab.model import download
import os
from PIL import Image

task_dict = {
        "body17":"checkpoints/body17.onnx",
        "body26":"checkpoints/body26.onnx",
        "wholebody133":"checkpoints/whole133.onnx",
        "face106":"checkpoints/face106.onnx",
        "hand21":"checkpoints/hand21.onnx",
        "bodydetect":"checkpoints/bodydetect.onnx",
        "cocodetect":"checkpoints/cocodetect.onnx",
}
class Workflow:
    @classmethod
    def support_task(cls):
        return list(task_dict.keys())
    @classmethod
    def _task_dict(cls):
        return task_dict
    @classmethod
    def coco_class(cls):
        return coco_class

    def __init__(self, task,checkpoint=None):
        self.task_dict = task_dict
        self.task_nick_name ={
            'hand':"hand21",
            'body':"body17",
            "wholebody":"wholebody133",
            "face":"face106",
        }
        if task in self.task_nick_name.keys():
            self.task = self.task_nick_name[task]
        else:
            self.task = task
        self.color_dict = {
            'red':[255,0,0],
            'orange':[255,125,0],
            'yellow':[255,255,0],
            'green':[0,255,0],
            'blue':[0,0,255],
            'purple':[255,0,255],
            'l_red':[128,0,0],
            'l_orange':[128,64,0],
            'l_yellow':[128,128,0],
            'l_green':[0,128,0],
            'l_blue':[0,0,128],
            'l_purple':[128,0,128],
        }
        if checkpoint is None: # 若不指定权重文件，则使用对应任务的默认模型
            checkpoint = self.task_dict[self.task]
            if not os.path.exists(checkpoint): # 下载默认模型
                print("本地未检测到{}任务对应模型，云端下载中...".format(self.task))
                path = "checkpoints"
                if not os.path.exists(path):
                    os.mkdir(path)
                model_name_map = {
                    "body17":"17 body keypoints",
                    "body26":"26 body keypoints",
                    "wholebody133":"133 wholebody keypoints",
                    "face106":"106 face keypoints",
                    "hand21":"21 hand keypoints",
                    "bodydetect":"body detection",
                    "cocodetect":"coco detection",
                }
                # download('test12318/bert-english',model_name=model_name,output=path)
                download(model_repo='XEdu123/xedu.hub_onnx_model', model_name=model_name_map[self.task],output=path)
            # download()

        # model_path='rtmpose-ort/rtmpose-s-0b29a8.onnx'
        self.model = ort.InferenceSession(checkpoint, None)
        print("模型加载成功！")

    def inference(self,data=None,show=False,get_img=None,threshold=0.3,bbox=None,target_class=None):
        self._get_img = get_img
        if self.task in ["body17","body26","face106","hand21","wholebody133"]:
            return self._pose_inference(data,show,get_img,bbox)
        elif self.task in['bodydetect','cocodetect']:
            return self._det_infer(data,show,get_img,threshold,target_class)
            # return self._det_inference(data,show,get_img)

    def _det_infer(self,data=None,show=False,get_img=None,threshold=0.65,target_class=None):
        
        from PIL import Image
        def preprocess(input_data):
            # convert the input data into the float32 input
            img_data = input_data.astype('float32')

            #normalize
            mean_vec = np.array([0.485, 0.456, 0.406])
            stddev_vec = np.array([0.229, 0.224, 0.225])
            norm_img_data = np.zeros(img_data.shape).astype('float32')
            for i in range(img_data.shape[0]):
                norm_img_data[i,:,:] = (img_data[i,:,:]/255 - mean_vec[i]) / stddev_vec[i]

            #add batch channel
            norm_img_data = norm_img_data.reshape(1, 3, 224, 224).astype('float32')
            return norm_img_data

        ### 读取模型
        model = self.model
        # session = ort.InferenceSession('rtmdet-acc0de.onnx', None)
        #注 实际根据不同的推理需求例如 TensorRT,CUDA,等需要更多设置，具体参考官网

        ### 准备数据
        # img_path = 'pose2.jpg'
        if isinstance(data,str):
            # image = plt.imread(data)
            # image = Image.open(data)
            image = cv2.imread(data)
        else:
            image = data
            # image = Image.fromarray(data)
        # image = Image.open(img_path).resize((224,224))  # 这里设置的动态数据尺寸，不需要resize
        re_image =cv2.resize(image,(224,224))
        re_image_data = np.array(re_image).transpose(2, 0, 1)
        input_data = preprocess(re_image_data)

        ### 推理
        raw_result = model.run([], {'input': input_data})
        # print(raw_result[1])
        ### 后处理
        h_ratio =  image.shape[0] /224
        w_ratio =  image.shape[1] /224 
        self.bboxs = []
        self.scores = []
        self.classes = []
        for (idx,[a,b,c,d,e]) in enumerate(raw_result[0][0]):#,raw_result[1][0]:
            if target_class is not None:
                if isinstance(target_class,str):    
                    if coco_class[raw_result[1][0][idx]+1] != target_class:
                        continue
                elif isinstance(target_class,List):
                    if coco_class[raw_result[1][0][idx]+1] not in  target_class:
                        continue
            if e> threshold:                    
                bbox = [a*w_ratio,b*h_ratio,c*w_ratio,d*h_ratio]
                self.bboxs.append(bbox)
                self.scores.append(e)
                self.classes.append(coco_class[raw_result[1][0][idx]+1])
        if get_img:
            if get_img =='cv2':
                for [a,b,c,d] in self.bboxs:
                    cv2.rectangle(image, (int(a),int(b)),(int(c),int(d)),(0,0,255),2)
            elif get_img =='pil':
                # image = cv2.cvtcolor(image,cv2.BGR2RGB)
                for [a,b,c,d] in self.bboxs:
                    cv2.rectangle(image, (int(a),int(b)),(int(c),int(d)),(0,0,255),2)
                image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            if show:
                self.show(image)
            return np.array(self.bboxs),image
        return np.array(self.bboxs)
        
    def _det_inference(self,data=None,show=False,get_img=None):
        if isinstance(data,str):
            img = plt.imread(data)
        else:
            img = data
        model = self.model
        # print(model.get_inputs()[0].shape)
        h, w,c = model.get_inputs()[0].shape[1:]
        print("hwc",img.shape,h,w,c)
        # img = np.resize(img,(h,w,c))
        # print(img.shape)
        input_tensor = [img.transpose(2,0,1)]
        # input_tensor = [img.transpose(2,0,1)]
        input_name = model.get_inputs()[0].name
        output_names = [o.name for o in model.get_outputs()]

        outputs = model.run(output_names,{input_name:input_tensor})
        np.set_printoptions(threshold=np.inf)
        np.set_printoptions(suppress=np.inf)
        # print(outputs)

        bo = outputs[0]
        bboxs = bo[:,:,:4][0]
        scores = bo[:,:,4][0]
        print(bboxs.shape,scores.shape)
        # print(scores)
        bboxs, scores = nms(bboxs,scores, 0.65)
        print(bboxs.shape,scores.shape)
        print(scores[:5000])
        # conf = bo[:,:,4]
        # bo = bo[0]
        # ind = conf.argsort()
        # # print("a",ind[:,:10])
        # # print(outputs[0].shape)
        # result = bo[ind[0]]
        # print(result[-10:])
        # result = outputs[0][bo>0.999]
        return bboxs[:5], scores[:5]# [-100:]

    def _pose_inference(self,data=None,show=False,get_img=None,bbox=None):
        model = self.model
        self.bbox=bbox
        h, w = model.get_inputs()[0].shape[2:]
        model_input_size = (w, h)
        # image_path='rtmpose-ort/000000147979.jpg'
        if isinstance(data,str):
            img = plt.imread(data)
        else:
            img = data
        # 前处理
        # start_time = time.time()
        self.data = data
        resized_img, center, scale = mmpose_preprocess(img, model_input_size,bbox)
        input_tensor = [resized_img.transpose(2, 0, 1)]
        input_name = model.get_inputs()[0].name
        output_names = [o.name for o in model.get_outputs()]
        # end_time = time.time()
        # print('前处理耗时：',end_time-start_time)
        # 模型推理
        # start_time = time.time()
        outputs = model.run(output_names, {input_name: input_tensor})
        # end_time = time.time()
        # print('推理耗时：',end_time-start_time)
        # 后处理
        # start_time = time.time()
        self.keypoints, self.scores = mmpose_postprocess(outputs, model_input_size, center, scale)
        # end_time = time.time()
        # print('后处理耗时：',end_time-start_time)
        # print('推理结果：')
        # print(keypoints)
        if get_img:
            # 绘制查看效果
            if get_img =='cv2':
                re = self._get_cv2_image()
            else:
                re = self._get_image()
            if show:
                self.show(re)
            return self.keypoints, re
        return self.keypoints
    
    def _get_cv2_image(self):
        sketch = {}
        if self.task == 'hand21':
            sketch = {
                'red':[[0,1],[1,2],[2,3],[3,4]],
                'orange':[[0,5],[5,6],[6,7],[7,8]],
                'yellow':[[0,9],[9,10],[10,11],[11,12]],
                'green':[[0,13],[13,14],[14,15],[15,16]],
                'blue':[[0,17],[17,18],[18,19],[19,20]]
            }
        elif self.task =='body26':
            sketch = {
                'red':[[0,1],[1,2],[2,0],[2,4],[1,3],[0,17],[0,18]],
                'orange':[[18,6],[8,6],[10,8]],
                'yellow':[[18,19],[19,12],[19,11]],
                'green':[[12,14],[14,16],[16,23],[21,16],[25,16]],
                'blue':[[11,13],[13,15],[15,20],[15,22],[15,24]],
                'purple':[[18,5],[5,7],[7,9]],
            }
        elif self.task =='body17':
            sketch = {
                'red':[[0,1],[1,2],[2,0],[2,4],[1,3],[4,6],[3,5]],
                'orange':[[10,8],[8,6]],
                'yellow':[[5,6],[6,12],[12,11],[11,5]],
                'green':[[12,14],[14,16]],
                'blue':[[11,13],[13,15]],
                'purple':[[5,7],[9,7]],
            }
        elif self.task=='wholebody133':
            sketch = {
                # body
                'red':[[0,1],[1,2],[2,0],[2,4],[1,3],[4,6],[3,5]],
                'orange':[[10,8],[8,6]],
                'yellow':[[5,6],[6,12],[12,11],[11,5]],
                'green':[[12,14],[14,16]],
                'blue':[[11,13],[13,15]],
                'purple':[[5,7],[9,7]],
            }
        elif self.task=='face106':
            sketch = {
                # 'green':[[51,52],[52,53],
                #         [57,58],[58,59],[59,60],[60,61],[61,62],[62,63]
                #     ]
            }
        if isinstance(self.data,str):
            img = cv2.imread((self.data))
        else:
            img = self.data
        # h,w,c = img.shape
        
        for j in range(self.keypoints.shape[0]):
            for i in range(self.keypoints.shape[1]):
                # plt.scatter(self.keypoints[j][i][0],self.keypoints[j][i][1],c='b',s=10)
                x1,y1 = self.keypoints[j][i]
                if self.bbox is not None:
                    sx1,sy1,sx2,sy2 = self.bbox # 
                    if sx1<x1<sx2 and sy1<y1<sy2 :
                        cv2.circle(img,(int(self.keypoints[j][i][0]),int(self.keypoints[j][i][1])),radius=1,color=[0,255,0])
                else:
                    cv2.circle(img,(int(self.keypoints[j][i][0]),int(self.keypoints[j][i][1])),radius=1,color=[0,255,0])
        for color in sketch.keys():
            # print(color,sketch[color])
            for [fx,fy] in sketch[color]:
                # plt.plot([self.keypoints[0][fx][0],self.keypoints[0][fy][0]],[self.keypoints[0][fx][1],self.keypoints[0][fy][1]],color=color)
                cv2.line(img, (int(self.keypoints[0][fx][0]),int(self.keypoints[0][fx][1])),(int(self.keypoints[0][fy][0]),int(self.keypoints[0][fy][1])),color=self.color_dict[color])

        return img

    def _get_image(self):
        sketch = {}
        if self.task == 'hand21':
            sketch = {
                'red':[[0,1],[1,2],[2,3],[3,4]],
                'orange':[[0,5],[5,6],[6,7],[7,8]],
                'yellow':[[0,9],[9,10],[10,11],[11,12]],
                'green':[[0,13],[13,14],[14,15],[15,16]],
                'blue':[[0,17],[17,18],[18,19],[19,20]]
            }
        elif self.task =='body26':
            sketch = {
                'red':[[0,1],[1,2],[2,0],[2,4],[1,3],[0,17],[0,18]],
                'orange':[[18,6],[8,6],[10,8]],
                'yellow':[[18,19],[19,12],[19,11]],
                'green':[[12,14],[14,16],[16,23],[21,16],[25,16]],
                'blue':[[11,13],[13,15],[15,20],[15,22],[15,24]],
                'purple':[[18,5],[5,7],[7,9]],
            }
        elif self.task =='body17':
            sketch = {
                'red':[[0,1],[1,2],[2,0],[2,4],[1,3],[4,6],[3,5]],
                'orange':[[10,8],[8,6]],
                'yellow':[[5,6],[6,12],[12,11],[11,5]],
                'green':[[12,14],[14,16]],
                'blue':[[11,13],[13,15]],
                'purple':[[5,7],[9,7]],
            }
        elif self.task =='wholebody133':
            sketch = {
                'red':[[0,1],[1,2],[2,0],[2,4],[1,3],[4,6],[3,5]],
                'orange':[[10,8],[8,6]],
                'yellow':[[5,6],[6,12],[12,11],[11,5]],
                'green':[[12,14],[14,16]],
                'blue':[[11,13],[13,15]],
                'purple':[[5,7],[9,7]],
            }
        import matplotlib.pyplot as plt
        fig = plt.gcf()
        canvas = fig.canvas
        # fig = plt.figure("Result")
        # canvas = fig.canvas
        if isinstance(self.data,str):
            img = plt.imread((self.data))
        else:
            img = self.data
        h,w,c = img.shape
        fig.set_size_inches(w/100,h/100)
        # print("self.data.shape",plt.imread(self.data).shape)
        plt.imshow(img)
        
        for j in range(self.keypoints.shape[0]):
            for i in range(self.keypoints.shape[1]):
                plt.scatter(self.keypoints[j][i][0],self.keypoints[j][i][1],c='b',s=10)
                # cv2.circle(img,(int(self.keypoints[j][i][0]),int(self.keypoints[j][i][1])),radius=1,color=[0,255,0])
        for color in sketch.keys():
            # print(color,sketch[color])
            for [fx,fy] in sketch[color]:
                plt.plot([self.keypoints[0][fx][0],self.keypoints[0][fy][0]],[self.keypoints[0][fx][1],self.keypoints[0][fy][1]],color=color)
                # cv2.line(img, (int(self.keypoints[0][fx][0]),int(self.keypoints[0][fx][1])),(int(self.keypoints[0][fy][0]),int(self.keypoints[0][fy][1])),color=self.color_dict[color])
        plt.axis('off')
        plt.subplots_adjust(top=1,bottom=0,right=1,left=0,hspace=0,wspace=0)
        plt.margins(0,0)
        img = img_from_canvas(canvas)
        if self._get_img == 'cv2':
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif self._get_img.lower() == 'pil':
            return img
        return img

    def show(self,img): # check
        if self._get_img.lower() == 'cv2':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif self._get_img.lower() == 'pil':
            img = img
        plt.imshow(img)
        plt.show()
    
    def save(self,img,save_path): # check
        if self._get_img == 'cv2':
            # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.imwrite(save_path,img)
        elif self._get_img.lower() == 'pil':
            img = img
            a = Image.fromarray(img)
            a.save(save_path)
            # plt.imshow(img)
            # plt.axis('off')
            # plt.subplots_adjust(top=1,bottom=0,right=1,left=0,hspace=0,wspace=0)
            # plt.margins(0,0)
            # plt.savefig(save_path)
    
    def format_output(self,language='zh'): # check
        if self.task in ["body17","body26","face106","hand21","wholebody133"]:
            formalize_keys = {
                "zh":["关键点坐标","分数"],
                "en":["keypoints","scores"],
                "ru":["ключевые точки","баллы"],
                "de":["Schlüsselpunkte","Partituren"],
                "fr":["points clés","partitions"]
            }
            formalize_result = {
                formalize_keys[language][0]:self.keypoints[0].tolist(),
                formalize_keys[language][1]:self.scores[0].tolist(),
            }
            # formalize_result = json.dumps(formalize_result, indent=4,sort_keys=False)
            pprint.pprint(formalize_result,sort_dicts=False)
        elif self.task in['bodydetect','cocodetect']:
            formalize_keys = {
                "zh":["检测框","分数","类别"],
                "en":['bounding boxes',"scores","class"],
                "ru":["ограничивающие рамки","баллы","занятия"],
                "de":["Begrenzungsrahmen","Partituren","Klassen"],
                "fr":["cadres de délimitation","partitions","Des classes"]
            }
            if self.classes is not None:
                formalize_result = {
                    formalize_keys[language][0]:self.bboxs,
                    formalize_keys[language][1]:self.scores,
                    formalize_keys[language][2]:self.classes,
                }
            else:
                formalize_result = {
                    formalize_keys[language][0]:self.bboxs,
                    formalize_keys[language][1]:self.scores,
                }
            pprint.pprint(formalize_result,sort_dicts=False)
        return formalize_result


def bbox_xyxy2cs(bbox: np.ndarray,
                 padding: float = 1.) -> Tuple[np.ndarray, np.ndarray]:
    """Transform the bbox format from (x,y,w,h) into (center, scale)

    Args:
        bbox (ndarray): Bounding box(es) in shape (4,) or (n, 4), formatted
            as (left, top, right, bottom)
        padding (float): BBox padding factor that will be multilied to scale.
            Default: 1.0

    Returns:
        tuple: A tuple containing center and scale.
        - np.ndarray[float32]: Center (x, y) of the bbox in shape (2,) or
            (n, 2)
        - np.ndarray[float32]: Scale (w, h) of the bbox in shape (2,) or
            (n, 2)
    """
    # convert single bbox from (4, ) to (1, 4)
    dim = bbox.ndim
    if dim == 1:
        bbox = bbox[None, :]

    # get bbox center and scale
    x1, y1, x2, y2 = np.hsplit(bbox, [1, 2, 3])
    center = np.hstack([x1 + x2, y1 + y2]) * 0.5
    scale = np.hstack([x2 - x1, y2 - y1]) * padding

    if dim == 1:
        center = center[0]
        scale = scale[0]

    return center, scale

def value2list(value: Any, valid_type: Union[Type, Tuple[Type, ...]],
               expand_dim: int) -> List[Any]:
    """If the type of ``value`` is ``valid_type``, convert the value to list
    and expand to ``expand_dim``.

    Args:
        value (Any): value.
        valid_type (Union[Type, Tuple[Type, ...]): valid type.
        expand_dim (int): expand dim.

    Returns:
        List[Any]: value.
    """
    if isinstance(value, valid_type):
        value = [value] * expand_dim
    return value


def check_type(name: str, value: Any,
               valid_type: Union[Type, Tuple[Type, ...]]) -> None:
    """Check whether the type of value is in ``valid_type``.

    Args:
        name (str): value name.
        value (Any): value.
        valid_type (Type, Tuple[Type, ...]): expected type.
    """
    if not isinstance(value, valid_type):
        raise TypeError(f'`{name}` should be {valid_type} '
                        f' but got {type(value)}')


def check_length(name: str, value: Any, valid_length: int) -> None:
    """If type of the ``value`` is list, check whether its length is equal with
    or greater than ``valid_length``.

    Args:
        name (str): value name.
        value (Any): value.
        valid_length (int): expected length.
    """
    if isinstance(value, list):
        if len(value) < valid_length:
            raise AssertionError(
                f'The length of {name} must equal with or '
                f'greater than {valid_length}, but got {len(value)}')


def check_type_and_length(name: str, value: Any,
                          valid_type: Union[Type, Tuple[Type, ...]],
                          valid_length: int) -> None:
    """Check whether the type of value is in ``valid_type``. If type of the
    ``value`` is list, check whether its length is equal with or greater than
    ``valid_length``.

    Args:
        value (Any): value.
        legal_type (Type, Tuple[Type, ...]): legal type.
        valid_length (int): expected length.

    Returns:
        List[Any]: value.
    """
    check_type(name, value, valid_type)
    check_length(name, value, valid_length)


def color_val_matplotlib(
    colors: Union[str, tuple, List[Union[str, tuple]]]
) -> Union[str, tuple, List[Union[str, tuple]]]:
    """Convert various input in RGB order to normalized RGB matplotlib color
    tuples,
    Args:
        colors (Union[str, tuple, List[Union[str, tuple]]]): Color inputs
    Returns:
        Union[str, tuple, List[Union[str, tuple]]]: A tuple of 3 normalized
        floats indicating RGB channels.
    """
    if isinstance(colors, str):
        return colors
    elif isinstance(colors, tuple):
        assert len(colors) == 3
        for channel in colors:
            assert 0 <= channel <= 255
        colors = [channel / 255 for channel in colors]
        return tuple(colors)
    elif isinstance(colors, list):
        colors = [
            color_val_matplotlib(color)  # type:ignore
            for color in colors
        ]
        return colors
    else:
        raise TypeError(f'Invalid type for color: {type(colors)}')


def color_str2rgb(color: str) -> tuple:
    """Convert Matplotlib str color to an RGB color which range is 0 to 255,
    silently dropping the alpha channel.

    Args:
        color (str): Matplotlib color.

    Returns:
        tuple: RGB color.
    """
    import matplotlib
    rgb_color: tuple = matplotlib.colors.to_rgb(color)
    rgb_color = tuple(int(c * 255) for c in rgb_color)
    return rgb_color


def convert_overlay_heatmap(feat_map: np.ndarray,
                            img: Optional[np.ndarray] = None,
                            alpha: float = 0.5) -> np.ndarray:
    """Convert feat_map to heatmap and overlay on image, if image is not None.

    Args:
        feat_map (np.ndarray): The feat_map to convert
            with of shape (H, W), where H is the image height and W is
            the image width.
        img (np.ndarray, optional): The origin image. The format
            should be RGB. Defaults to None.
        alpha (float): The transparency of featmap. Defaults to 0.5.

    Returns:
        np.ndarray: heatmap
    """
    assert feat_map.ndim == 2 or (feat_map.ndim == 3
                                  and feat_map.shape[0] in [1, 3])
    if feat_map.ndim == 3:
        feat_map = feat_map.transpose(1, 2, 0)

    norm_img = np.zeros(feat_map.shape)
    norm_img = cv2.normalize(feat_map, norm_img, 0, 255, cv2.NORM_MINMAX)
    norm_img = np.asarray(norm_img, dtype=np.uint8)
    heat_img = cv2.applyColorMap(norm_img, cv2.COLORMAP_JET)
    heat_img = cv2.cvtColor(heat_img, cv2.COLOR_BGR2RGB)
    if img is not None:
        heat_img = cv2.addWeighted(img, 1 - alpha, heat_img, alpha, 0)
    return heat_img


def wait_continue(figure, timeout: float = 0, continue_key: str = ' ') -> int:
    """Show the image and wait for the user's input.

    This implementation refers to
    https://github.com/matplotlib/matplotlib/blob/v3.5.x/lib/matplotlib/_blocking_input.py

    Args:
        timeout (float): If positive, continue after ``timeout`` seconds.
            Defaults to 0.
        continue_key (str): The key for users to continue. Defaults to
            the space key.

    Returns:
        int: If zero, means time out or the user pressed ``continue_key``,
            and if one, means the user closed the show figure.
    """  # noqa: E501
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import CloseEvent
    is_inline = 'inline' in plt.get_backend()
    if is_inline:
        # If use inline backend, interactive input and timeout is no use.
        return 0

    if figure.canvas.manager:  # type: ignore
        # Ensure that the figure is shown
        figure.show()  # type: ignore

    while True:

        # Connect the events to the handler function call.
        event = None

        def handler(ev):
            # Set external event variable
            nonlocal event
            # Qt backend may fire two events at the same time,
            # use a condition to avoid missing close event.
            event = ev if not isinstance(event, CloseEvent) else event
            figure.canvas.stop_event_loop()

        cids = [
            figure.canvas.mpl_connect(name, handler)  # type: ignore
            for name in ('key_press_event', 'close_event')
        ]

        try:
            figure.canvas.start_event_loop(timeout)  # type: ignore
        finally:  # Run even on exception like ctrl-c.
            # Disconnect the callbacks.
            for cid in cids:
                figure.canvas.mpl_disconnect(cid)  # type: ignore

        if isinstance(event, CloseEvent):
            return 1  # Quit for close.
        elif event is None or event.key == continue_key:
            return 0  # Quit for continue.


def img_from_canvas(canvas: 'FigureCanvasAgg') -> np.ndarray:
    """Get RGB image from ``FigureCanvasAgg``.

    Args:
        canvas (FigureCanvasAgg): The canvas to get image.

    Returns:
        np.ndarray: the output of image in RGB.
    """
    s, (width, height) = canvas.print_to_buffer()
    buffer = np.frombuffer(s, dtype='uint8')
    img_rgba = buffer.reshape(height, width, 4)
    rgb, alpha = np.split(img_rgba, [3], axis=2)
    return rgb.astype('uint8')

def load_json_log(json_log):
    """load and convert json_logs to log_dicts.

    Args:
        json_log (str): The path of the json log file.

    Returns:
        dict: The result dict contains two items, "train" and "val", for
        the training log and validate log.

    Example:
        An example output:

        .. code-block:: python

            {
                'train': [
                    {"lr": 0.1, "time": 0.02, "epoch": 1, "step": 100},
                    {"lr": 0.1, "time": 0.02, "epoch": 1, "step": 200},
                    {"lr": 0.1, "time": 0.02, "epoch": 1, "step": 300},
                    ...
                ]
                'val': [
                    {"accuracy/top1": 32.1, "step": 1},
                    {"accuracy/top1": 50.2, "step": 2},
                    {"accuracy/top1": 60.3, "step": 2},
                    ...
                ]
            }
    """
    log_dict = dict(train=[], val=[])
    with open(json_log, 'r') as log_file:
        for line in log_file:
            log = json.loads(line.strip())
            # A hack trick to determine whether the line is training log.
            mode = 'train' if 'lr' in log else 'val'
            log_dict[mode].append(log)

    return log_dict

def _fix_aspect_ratio(bbox_scale: np.ndarray,
                      aspect_ratio: float) -> np.ndarray:
    """Extend the scale to match the given aspect ratio.

    Args:
        scale (np.ndarray): The image scale (w, h) in shape (2, )
        aspect_ratio (float): The ratio of ``w/h``

    Returns:
        np.ndarray: The reshaped image scale in (2, )
    """
    w, h = np.hsplit(bbox_scale, [1])
    bbox_scale = np.where(w > h * aspect_ratio,
                          np.hstack([w, w / aspect_ratio]),
                          np.hstack([h * aspect_ratio, h]))
    return bbox_scale

def _rotate_point(pt: np.ndarray, angle_rad: float) -> np.ndarray:
    """Rotate a point by an angle.

    Args:
        pt (np.ndarray): 2D point coordinates (x, y) in shape (2, )
        angle_rad (float): rotation angle in radian

    Returns:
        np.ndarray: Rotated point in shape (2, )
    """
    sn, cs = np.sin(angle_rad), np.cos(angle_rad)
    rot_mat = np.array([[cs, -sn], [sn, cs]])
    return rot_mat @ pt

def _get_3rd_point(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """To calculate the affine matrix, three pairs of points are required. This
    function is used to get the 3rd point, given 2D points a & b.

    The 3rd point is defined by rotating vector `a - b` by 90 degrees
    anticlockwise, using b as the rotation center.

    Args:
        a (np.ndarray): The 1st point (x,y) in shape (2, )
        b (np.ndarray): The 2nd point (x,y) in shape (2, )

    Returns:
        np.ndarray: The 3rd point.
    """
    direction = a - b
    c = b + np.r_[-direction[1], direction[0]]
    return c

def get_warp_matrix(center: np.ndarray,
                    scale: np.ndarray,
                    rot: float,
                    output_size: Tuple[int, int],
                    shift: Tuple[float, float] = (0., 0.),
                    inv: bool = False) -> np.ndarray:
    """Calculate the affine transformation matrix that can warp the bbox area
    in the input image to the output size.

    Args:
        center (np.ndarray[2, ]): Center of the bounding box (x, y).
        scale (np.ndarray[2, ]): Scale of the bounding box
            wrt [width, height].
        rot (float): Rotation angle (degree).
        output_size (np.ndarray[2, ] | list(2,)): Size of the
            destination heatmaps.
        shift (0-100%): Shift translation ratio wrt the width/height.
            Default (0., 0.).
        inv (bool): Option to inverse the affine transform direction.
            (inv=False: src->dst or inv=True: dst->src)

    Returns:
        np.ndarray: A 2x3 transformation matrix
    """
    shift = np.array(shift)
    src_w = scale[0]
    dst_w = output_size[0]
    dst_h = output_size[1]

    # compute transformation matrix
    rot_rad = np.deg2rad(rot)
    src_dir = _rotate_point(np.array([0., src_w * -0.5]), rot_rad)
    dst_dir = np.array([0., dst_w * -0.5])

    # get four corners of the src rectangle in the original image
    src = np.zeros((3, 2), dtype=np.float32)
    src[0, :] = center + scale * shift
    src[1, :] = center + src_dir + scale * shift
    src[2, :] = _get_3rd_point(src[0, :], src[1, :])

    # get four corners of the dst rectangle in the input image
    dst = np.zeros((3, 2), dtype=np.float32)
    dst[0, :] = [dst_w * 0.5, dst_h * 0.5]
    dst[1, :] = np.array([dst_w * 0.5, dst_h * 0.5]) + dst_dir
    dst[2, :] = _get_3rd_point(dst[0, :], dst[1, :])

    if inv:
        warp_mat = cv2.getAffineTransform(np.float32(dst), np.float32(src))
    else:
        warp_mat = cv2.getAffineTransform(np.float32(src), np.float32(dst))

    return warp_mat

def top_down_affine(input_size: dict, bbox_scale: dict, bbox_center: dict,
                    img: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Get the bbox image as the model input by affine transform.

    Args:
        input_size (dict): The input size of the model.
        bbox_scale (dict): The bbox scale of the img.
        bbox_center (dict): The bbox center of the img.
        img (np.ndarray): The original image.

    Returns:
        tuple: A tuple containing center and scale.
        - np.ndarray[float32]: img after affine transform.
        - np.ndarray[float32]: bbox scale after affine transform.
    """
    w, h = input_size
    warp_size = (int(w), int(h))

    # reshape bbox to fixed aspect ratio
    bbox_scale = _fix_aspect_ratio(bbox_scale, aspect_ratio=w / h)

    # get the affine matrix
    center = bbox_center
    scale = bbox_scale
    rot = 0
    warp_mat = get_warp_matrix(center, scale, rot, output_size=(w, h))

    # do affine transform
    img = cv2.warpAffine(img, warp_mat, warp_size, flags=cv2.INTER_LINEAR)

    return img, bbox_scale

def mmpose_preprocess(
    img: np.ndarray, input_size: Tuple[int, int] = (192, 256),bbox=None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Do preprocessing for RTMPose model inference.

    Args:
        img (np.ndarray): Input image in shape.
        input_size (tuple): Input image size in shape (w, h).

    Returns:
        tuple:
        - resized_img (np.ndarray): Preprocessed image.
        - center (np.ndarray): Center of image.
        - scale (np.ndarray): Scale of image.
    """
    # get shape of image
    img_shape = img.shape[:2]
    if bbox is None:
        bbox = np.array([0, 0, img_shape[1], img_shape[0]])

    # get center and scale
    center, scale = bbox_xyxy2cs(bbox, padding=1.25)

    # do affine transformation
    resized_img, scale = top_down_affine(input_size, scale, center, img)

    # normalize image
    mean = np.array([123.675, 116.28, 103.53])
    std = np.array([58.395, 57.12, 57.375])
    resized_img = (resized_img - mean) / std

    return resized_img, center, scale

def get_simcc_maximum(simcc_x: np.ndarray,
                      simcc_y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Get maximum response location and value from simcc representations.

    Note:
        instance number: N
        num_keypoints: K
        heatmap height: H
        heatmap width: W

    Args:
        simcc_x (np.ndarray): x-axis SimCC in shape (K, Wx) or (N, K, Wx)
        simcc_y (np.ndarray): y-axis SimCC in shape (K, Wy) or (N, K, Wy)

    Returns:
        tuple:
        - locs (np.ndarray): locations of maximum heatmap responses in shape
            (K, 2) or (N, K, 2)
        - vals (np.ndarray): values of maximum heatmap responses in shape
            (K,) or (N, K)
    """
    N, K, Wx = simcc_x.shape
    simcc_x = simcc_x.reshape(N * K, -1)
    simcc_y = simcc_y.reshape(N * K, -1)

    # get maximum value locations
    x_locs = np.argmax(simcc_x, axis=1)
    y_locs = np.argmax(simcc_y, axis=1)
    locs = np.stack((x_locs, y_locs), axis=-1).astype(np.float32)
    max_val_x = np.amax(simcc_x, axis=1)
    max_val_y = np.amax(simcc_y, axis=1)

    # get maximum value across x and y axis
    mask = max_val_x > max_val_y
    max_val_x[mask] = max_val_y[mask]
    vals = max_val_x
    locs[vals <= 0.] = -1

    # reshape
    locs = locs.reshape(N, K, 2)
    vals = vals.reshape(N, K)

    return locs, vals

def mmpose_decode(simcc_x: np.ndarray, simcc_y: np.ndarray,
           simcc_split_ratio) -> Tuple[np.ndarray, np.ndarray]:
    """Modulate simcc distribution with Gaussian.

    Args:
        simcc_x (np.ndarray[K, Wx]): model predicted simcc in x.
        simcc_y (np.ndarray[K, Wy]): model predicted simcc in y.
        simcc_split_ratio (int): The split ratio of simcc.

    Returns:
        tuple: A tuple containing center and scale.
        - np.ndarray[float32]: keypoints in shape (K, 2) or (n, K, 2)
        - np.ndarray[float32]: scores in shape (K,) or (n, K)
    """
    keypoints, scores = get_simcc_maximum(simcc_x, simcc_y)
    keypoints /= simcc_split_ratio

    return keypoints, scores

def mmpose_postprocess(outputs: List[np.ndarray],
                model_input_size: Tuple[int, int],
                center: Tuple[int, int],
                scale: Tuple[int, int],
                simcc_split_ratio: float = 2.0
                ) -> Tuple[np.ndarray, np.ndarray]:
    """Postprocess for RTMPose model output.

    Args:
        outputs (np.ndarray): Output of RTMPose model.
        model_input_size (tuple): RTMPose model Input image size.
        center (tuple): Center of bbox in shape (x, y).
        scale (tuple): Scale of bbox in shape (w, h).
        simcc_split_ratio (float): Split ratio of simcc.

    Returns:
        tuple:
        - keypoints (np.ndarray): Rescaled keypoints.
        - scores (np.ndarray): Model predict scores.
    """
    # use simcc to decode
    simcc_x, simcc_y = outputs
    keypoints, scores = mmpose_decode(simcc_x, simcc_y, simcc_split_ratio)

    # rescale keypoints
    keypoints = keypoints / model_input_size * scale + center - scale / 2

    return keypoints, scores

coco_class = {
    1: "person",
    2: "bicycle",
    3:"car",
    4:"motorcycle",
    5:"airplane",
    6:"bus",
    7:"train",
    8:"truck",
    9:"boat",
    10:"traffic light",
    11:"fire hydrant",
    12:"street sign",
    13:"stop sign",
    14:"parking meter",
    15:"bench",
    16:"bird",
    17:"cat",
    18:"dog",
    19:"horse",
    20:"sheep",
    21:"cow",
    22:"elephant",
    23:"bear",
    24:"zebra",
    25:"giraffe",
    26:"hat",
    27:"backpack",
    28:"umbrella",
    29:"shoe",
    30:"eye glasses",
    31:"handbag",
    32:"tie",
    33:"suitcase",
    34:"frisbee",
    35:"skis",
    36:"snowboard",
    37:"sports ball",
    38:"kite",
    39:"baseball bat",
    40:"baseball glove",
    41:"skateboard",
    42:"surfboard",
    43:"tennis racket",
    44:"bottle",
    45:"plate",
    46:"wine glass",
    47:"cup",
    48:"fork",
    49:"knife",
    50:"spoon",
    51:"bowl",
    52:"banana",
    53:"apple",
    54:"sandwich",
    55:"orange",
    56:"broccoli",
    57:"carrot",
    58:"hot dog",
    59:"pizza",
    60:"donut",
    61:"cake",
    62:"chair",
    63:"couch",
    64:"potted plant",
    65:"bed",
    66:"mirror",
    67:"dining table",
    68:"window",
    69:"desk",
    70:"toilet",
    71:"door",
    72:"tv",
    73:"laptop",
    74:"mouse",
    75:"remote",
    76:"keyboard",
    77:"cell phone",
    78:"microwave",
    79:"oven",
    80:"toaster",
    81:"sink",
    82:"refrigerator",
    83:"blender",
    84:"book",
    85:"clock",
    86:"vase",
    87:"scissors",
    88:"teddy bear",
    89:"hair drier",
    90:"toothbrush",
}