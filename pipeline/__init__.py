# Makes pipeline/ a Python package.
# All custom modules (loader, keypoints, masking, blending, motion_transfer)
# are imported from here so other files can do:
#   from pipeline.loader import load_checkpoints
#   from pipeline.keypoints import temporal_smooth
#   etc.