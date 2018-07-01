git clone git@github.com:tensorflow/models.git

python -m locatus.iv3_train.py --image_dir ../results/locatus/train/
python -m locatus.iv3_classify.py \
--graph=/tmp/output_graph.pb --labels=/tmp/output_labels.txt \
--input_layer=Placeholder \
--output_layer=final_result \
--image=../results/locatus/10000/10000.png
