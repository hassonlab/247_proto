protocnew -I=. --python_out=. data.proto

python add_patient.py --project tfs --subject 625 --data_dir /projects/HASSON/247/data/conversations-car
python add_patient.py --project podcast --subject 717 --data_dir /projects/HASSON/247/data/podcast-data