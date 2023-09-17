
# Project Title

Pose Detection Python Package


## Installation

Install my-project with npm

```bash
  pip install pose-detection
```
    
## Demo

from posedr import run_pose_detection

# Run pose detection with default parameters
run_pose_detection()

# You can also customize the parameters
run_pose_detection(mode=True, smooth=False, detectionCon=0.7, trackCon=0.8)

Parameters:

mode (bool, optional): Set to True for static image mode. Default is False.

smooth (bool, optional): Enable landmark smoothing. Default is True.

detectionCon (float, optional): Minimum detection confidence threshold. Default is 0.5.

trackCon (float, optional): Minimum tracking confidence threshold. Default is 0.5.




## License

This project is licensed under the MIT License - see the LICENSE file for details.

