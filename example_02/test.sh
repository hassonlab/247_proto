protocnew -I=. --python_out=. patient_info.proto

python add_patient.py --project tfs --subject 625 --data_dir /projects/HASSON/247/data/conversations-car
python list_patient.py --input_file tfs_625.pb

# python add_patient.py --project podcast --subject 661 --data_dir /projects/HASSON/247/data/podcast-data
# python list_patient.py --input_file podcast_661.pb