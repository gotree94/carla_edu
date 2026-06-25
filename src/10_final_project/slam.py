import numpy as np
import cv2

class SimpleVisualSLAM:
    def __init__(self):
        self.orb = cv2.ORB_create(nfeatures=1000)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        self.keypoints = []
        self.descriptors = []
        self.poses = []
        self.map_points = []

        self.prev_kp = None
        self.prev_desc = None
        self.prev_pose = np.eye(4)

        self.FX = self.FY = 500.0
        self.CX = 320.0
        self.CY = 240.0
        self.K = np.array([
            [self.FX, 0, self.CX],
            [0, self.FY, self.CY],
            [0, 0, 1]
        ])

    def process_frame(self, rgb_image, timestamp=0.0):
        gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)

        kp, desc = self.orb.detectAndCompute(gray, None)

        result = {
            'keypoints': kp,
            'descriptors': desc,
            'tracked': 0,
            'pose': self.prev_pose.copy(),
            'features_img': None
        }

        if self.prev_desc is not None and desc is not None and len(desc) > 10:
            matches = self.bf.match(self.prev_desc, desc)
            matches = sorted(matches, key=lambda x: x.distance)[:50]

            if len(matches) >= 8:
                pts_prev = np.float32([
                    self.prev_kp[m.queryIdx].pt for m in matches
                ]).reshape(-1, 2)
                pts_curr = np.float32([
                    kp[m.trainIdx].pt for m in matches
                ]).reshape(-1, 2)

                E, mask = cv2.findEssentialMat(
                    pts_curr, pts_prev, self.K,
                    method=cv2.RANSAC, prob=0.999, threshold=1.0
                )

                if E is not None and mask is not None:
                    _, R, t, mask_pose = cv2.recoverPose(
                        E, pts_curr, pts_prev, self.K
                    )

                    delta = np.eye(4)
                    delta[:3, :3] = R
                    delta[:3, 3] = t.flatten()
                    self.prev_pose = self.prev_pose @ np.linalg.inv(delta)

                    result['pose'] = self.prev_pose.copy()
                    result['tracked'] = np.sum(mask)

        self.prev_kp = kp
        self.prev_desc = desc
        self.poses.append(self.prev_pose.copy())

        img_vis = rgb_image.copy()
        if kp:
            cv2.drawKeypoints(img_vis, kp, img_vis, color=(0, 255, 0))
        result['features_img'] = img_vis

        return result

    def get_trajectory(self):
        return np.array([p[:3, 3] for p in self.poses])
