from sentence_transformers import SentenceTransformer, util

import numpy as np
import tensorflow as tf
import spacy
import torch

from glob import glob
import csv
import json
import os

class myModel:
    def __init__(self) -> None:
        # Load nlp model
        print("Loading NLP model...")
        self.nlp = spacy.load('en_core_web_lg')
        
        # Extract CLIP embeddings from local files
        print("Extracting CLIP embeddings...")
        clip_paths = glob('./clip-features-vit-b32\\*.npy')
        clip_embeddings = np.load(clip_paths[0])
        for path in clip_paths[1:]:
            c_vector = np.load(path)
            clip_embeddings = np.append(clip_embeddings, c_vector, axis=0)
        self.clip_embeddings = clip_embeddings.astype(np.float32)
        
        #Extract concept CLIP embeddings from local files
        print("Extracting concepts embeddings...")
        concept_paths = glob('./CLIP_concepts/*.npy')
        concept_embeddings = np.load(concept_paths[0])
        for path in concept_paths[1:]:
            c_vector = np.load(path)
            concept_embeddings = np.append(concept_embeddings, c_vector, axis=0)
        self.concept_embeddings = concept_embeddings.astype(np.float32)
        
        # Create list of keyframes ids and corresponding video
        print("Mapping keyframes...")
        objects_paths = glob('./objects_filtered\\*\\*.json')
        self.keyframe_names = []
        for path in objects_paths:
            vid_frameid = [path.split('\\')[-2], path.split('\\')[-1].split('.')[0]]
            self.keyframe_names.append(vid_frameid)
        
        # Initialize CLIP model
        print("Loading CLIP model...")
        self.clip_model = SentenceTransformer('clip-ViT-B-32')
        return
    
    def _clip_search(self, query, k=5):
        #Initialize model
        # clip_model = SentenceTransformer('clip-ViT-B-32')
        clip_model = self.clip_model
        
        query_emb = clip_model.encode([query], convert_to_tensor=True, show_progress_bar=False)
        
        hits = util.semantic_search(query_emb, self.clip_embeddings, top_k=k)[0]
        
        results = []
        for hit in hits:
            result = hit['corpus_id']
            results.append(result)
        return results
    
    def _concepts_filtering(self, clip_results, query, k=3):
        clip_model = self.clip_model
        
        query_emb = clip_model.encode([query], convert_to_tensor=True, show_progress_bar=False)
        
        concept_embeds = [self.concept_embeddings[x] for x in clip_results]
        
        concept_embeds = torch.tensor(concept_embeds)
        
        hits = util.semantic_search(query_emb, concept_embeds, top_k=k)[0]
        
        results = []
        for hit in hits:
            result = self.keyframe_names[clip_results[hit['corpus_id']]]
            results.append(result)
        return results

    def _objects_filtering(self, clip_results, query, k=3):
        # Extract subjects + objects from query
        query_objs = []
        doc = self.nlp(query)
        # for word in doc:
        #     if word.dep_ == "nsubj" or word.dep_ == "iobj" or word.dep_ == "dobj":
        #         query_objs.append(word)
        for chunk in doc.noun_chunks:
            query_objs.append(chunk)
        
        #Scoring
        scores = []
        for kf in clip_results:
            if int(kf[1]) <= 14:
                score=0
                scores.append(score)
                continue
            obj_path = './objects_filtered/' + kf[0] + '/' + kf[1] + '.json'
            with open(obj_path, 'r') as r_stream:
                obj = json.load(r_stream)
                score = 0
                
                for object, confidence in zip(obj["Objects"], obj["Scores"]):
                    sims = []
                    for query_obj in query_objs:
                        sims.append(self.nlp(object).similarity(query_obj))
                    similarity = max(sims)
                    score += similarity * float(confidence) #Score is sum of the similarity of the object to the query * confidence score
                    
                if len(obj["Objects"]) == 0: # Remain impartial to frames with no objects 
                    score = 0.5
            scores.append(score)
            
        #Get top k frames
        top_k = np.argsort(scores)[-k:]
        return [clip_results[x] for x in top_k]
    
    def predict(self, query, k=5):
        
        clip_results = self._clip_search(query, k*10)
        
        concept_results = self._concepts_filtering(clip_results, query, k*2)
        
        objects_results = self._objects_filtering(concept_results, query, k)
        
        #Mapping results to actual frame numbers
        final_results = []
        for result in objects_results:
            path = './map-keyframes/' + result[0] + '.csv'
            with open(path, 'r') as r_stream:
                csvreader = csv.reader(r_stream)
                next(csvreader) #Skip columns names
                
                for row in csvreader:
                    if int(row[0]) == int(result[1]):
                        # final_results.append([result[0], int(row[3]) + np.random.randint(-150,150)])
                        final_results.append([result[0], int(row[3]) + np.random.randint(1,5)])
                        break
        
        #Upload to csv file
        print("Prediction complete! Writing to csv file...")
        os.makedirs('./submission', exist_ok=True)
        with open('./submission/newest_result.csv', 'w', newline='') as w_stream:
            csvwriter = csv.writer(w_stream)
            csvwriter.writerows(final_results)
        print("Complete")
        
        #Map results to corresponding urls
        root_url = 'https://aichallenge2023.blob.core.windows.net/keyframes/'
        final_results = [] # Reinitialize
        for result in objects_results:
            temp = []
            f_url = root_url + result[0][1] + result[0][2] + '/keyframes/' + result[0] + '/' + result[1] + '.jpg'
            temp.append(f_url)
            with open('./metadata/' + result[0] + '.json', 'r', encoding="utf8") as r_stream:
                meta = json.load(r_stream)
                v_url = meta["watch_url"]
            with open('./map-keyframes/' + result[0] + '.csv', 'r') as r_stream:
                csvreader = csv.reader(r_stream)
                next(csvreader) #Skip columns names
                for row in csvreader:
                    if int(row[0]) == int(result[1]):
                        time = int(float(row[1]))
                        temp.append(v_url + '&t=' + str(time))
            final_results.append(temp)
        return final_results
            