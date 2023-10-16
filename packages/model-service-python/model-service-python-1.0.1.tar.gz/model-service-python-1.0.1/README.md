# model-service-python
A Python SDK for Model Service

This project currently in alpha testing, will open source the code soon.

```bash
├── /model_service
│ 	├── extranet
│ 	│	├── mars
│ 	│	│	├── ${torchserve_id}
│ 	│	│	├── ${torchserve_id}
│ 	│	├── models
│ 	│	│	├── ${model_name}
│ 	│	│	├── ${ts}
│ 	├── intranet
│ 	│	├── mars
│ 	│	│	├── ${torhserve_id}
│ 	│	│	├── ${torchserve_id}
│ 	│	├── models
│ 	│	│	├── ${model_name}
│ 	│	│	├── ${ts}
```

# Installation
## PyPi
https://pypi.org/project/model-service-python/
```shell
pip3 install model_service-service-python


scp -p 52822 root@172.17.84.60:/dm-esmm-seq/model_service/extranet/models/en_knowOutline_classify/1695004952 /Users/zsm/workspace/CVTE/bm/model-service-handler/en_knowOutline_classify
```

 ssh root@172.17.84.60 -p 52822