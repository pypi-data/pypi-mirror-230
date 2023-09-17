# from MMEdu import MMPose as pose
from XEdu.hub import Workflow as wf
wf.coco_class()
import time
import cv2

def pose_infer_demo():
    # a = time.time()
    img = 'pose1.jpg' # 指定进行推理的图片路径
    pose = wf(task='wholebody133')# ,checkpoint="rtmpose-m-80e511.onnx") # 实例化mmpose模型
    a = time.time()

    result,img = pose.inference(data=img,get_img='pil') # 在CPU上进行推理
    pose.show(img)
    pose.save(img,"pimg_ou.png")
    cv2.imwrite("pimg_ou_d.png",img)
    
    # rtmpose-m-80e511.onnx
    print(time.time()- a)
    pose.format_output(language="zh")
    # print(result)

def video_infer_demo():
    import numpy as np
    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("pose.mp4")
    
    pose = wf(task='face')#checkpoint="face_new.onnx") # 实例化mmpose模型
    det = wf(task='bodydetect')#,checkpoint='rtmdet-acc0de.onnx')# ,checkpoint="rtmpose-m-80e511.onnx") # 实例化mmpose模型

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        bboxs = det.inference(data=frame,threshold=0.3) # 在CPU上进行推理
        img = frame
        for i in bboxs:
            keypoints,img =pose.inference(data=img,get_img='cv2',bbox=i) # 在CPU上进行推理

        for [x1,y1,x2,y2] in bboxs:
            # print(x1,y1,x2,y2)
            cv2.rectangle(img, (int(x1),int(y1)),(int(x2),int(y2)),(0,255,0),2)
        # for j in range(keypoints.shape[0]):
        #     for i in range(keypoints.shape[1]):
        #         cv2.circle(frame, (int(keypoints[j][i][0]),int(keypoints[j][i][1])),5,(0,255,0),-1)
        cv2.imshow('video', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break    
    cap.release()
    cv2.destroyAllWindows()

def prune():
    import onnx 
    from onnxsim import simplify

    model = onnx.load('whole133.onnx')
    model,c= simplify(model)
    print(c)
    onnx.save(model,'whole133_p.onnx')

def merge():
    import onnx
    from onnxoptimizer import optimize
    model = onnx.load('whole133_p.onnx')
    passes = ['fuse_bn_into_conv']
    model = optimize(model,passes)

    onnx.save(model,'whole133_p_m.onnx')

def det_infer_demo():
    # a = time.time()
    from XEdu.hub import Workflow as wf
    import numpy as np
    img = 'pose4.jpg' # 指定进行推理的图片路径
    image = cv2.imread(img)
    print(image.shape)
    det = wf(task='bodydetect')#,checkpoint='rtmdet-acc0de.onnx')# ,checkpoint="rtmpose-m-80e511.onnx") # 实例化mmpose模型
    # pose = wf(task='det',checkpoint='rtmdet-acc0de.onnx')# ,checkpoint="rtmpose-m-80e511.onnx") # 实例化mmpose模型

    a = time.time()
    # image = cv2.resize(image,(640,640))
    bboxs,im_ou = det.inference(data=image,get_img='cv2',threshold=0.3,show=True) # 在CPU上进行推理
    print(im_ou.shape)
    cv2.imwrite("im_ou.png",im_ou)
    # print(bboxs)
    det.save(im_ou,"im_ou_d.jpg")
    print(time.time()- a)

    det.format_output(language="de")
    # print(result)

def hand_video_demo():
    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("pose.mp4")

    pose = wf(task='hand21')# ,checkpoint="rtmpose-m-80e511.onnx") # 实例化pose模型

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        keypoints,img =pose.inference(data=frame,get_img='cv2') # 在CPU上进行推理
        cv2.imshow('video', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break    
    cap.release()
    cv2.destroyAllWindows()

def coco_det_demo():
    # rtmdet-coco
    img = 'pose1.jpg' # 指定进行推理的图片路径
    det = wf(task='bodydetect' )#,checkpoint="rtmdet-coco.onnx") # 实例化mmpose模型
    a = time.time()

    result,img = det.inference(data=img,get_img='cv2') # 在CPU上进行推理
    # det.show(img)
    # det.save(img,"pimg_ou.png")
    
    # rtmpose-m-80e511.onnx
    print(time.time()- a)
    re = det.format_output(language="zh")
    print(re)

def face_det_demo():
    img = 'pose1.jpg' # 指定进行推理的图片路径
    det = wf(task='facedetect' )#,checkpoint="rtmdet-coco.onnx") # 实例化mmpose模型
    a = time.time()

    result,img = det.inference(data=img,get_img='cv2') # 在CPU上进行推理
    # det.show(img)
    # det.save(img,"pimg_ou.png")
    
    # rtmpose-m-80e511.onnx
    print(time.time()- a)
    re = det.format_output(language="zh")
    print(re)

if __name__ == "__main__":
    # pose_infer_demo()
    # det_infer_demo()
    # video_infer_demo()
    # hand_video_demo()
    # coco_det_demo()
    # print(wf.coco_class())
    face_det_demo()