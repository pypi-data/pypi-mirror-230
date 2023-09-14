from SpeakerDiarization import MySpeakerDiarization
import torch
def get_annotations(file):
    device= torch.device('cpu')
    pipeline = MySpeakerDiarization(  # define speaker diarization pipeline with pretrained modules
    #use_auth_token='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'
    )

    pipeline.to(device)

    pipeline.instantiate({ # the pipeline has to be instantiated with parameters before it is being used
        "segmentation": {
            "min_duration_off": 0.0,
            "threshold": 0.71
        },
        "clustering":{
            "method": "centroid",
            "min_cluster_size": 15,
            "threshold": 0.8
        }
    })

    annotations= pipeline(file)
    return annotations