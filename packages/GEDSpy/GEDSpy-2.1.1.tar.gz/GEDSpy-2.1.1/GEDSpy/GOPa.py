#Requirements import

import urllib.request 
import re
import pandas as pd
from tqdm import tqdm
import json
import zipfile
import requests
import gzip
import shutil
import numpy as np
from scipy import stats
import os
from bs4 import BeautifulSoup
import warnings
import copy
import networkx as nx
from pyvis.network import Network
import webbrowser
import tkinter as tk
from collections import Counter
from datetime import datetime
import pkg_resources
import matplotlib.pyplot as plt
from adjustText import adjust_text
from matplotlib.lines import Line2D
from scipy.cluster.hierarchy import linkage, dendrogram
import math


   

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

#Geta data directory


def get_package_directory():
    return pkg_resources.resource_filename(__name__, '')


_cwd = str(get_package_directory())

_path_inside = str(_cwd) + '/data'

_path_in_inside = str(_cwd) + '/data/in_use'

_path_tmp = str(_cwd) + '/data/tmp'

#Fucntions for data preparing

#zip data 

def compress_directory_to_zip(directory_path =  _path_inside, output_file = _cwd + '/data.zip'):
    # Create a zip compressed file
    with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the directory and its subdirectories
        for folder, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(folder, file)
                relative_path = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname=relative_path)




#Data downloading


def spec_dic(gene_dictionary, species):
    if species == 'human':
        tf_h = ['Homo sapiens' in x for x in gene_dictionary['species']]
        gene_dictionary_q = gene_dictionary[tf_h].copy()
        gene_dictionary_q = gene_dictionary_q.reset_index(drop = True)
    elif species == 'mouse':
        tf_h = ['Mus musculus' in x for x in gene_dictionary['species']]
        gene_dictionary_q = gene_dictionary[tf_h].copy()
        gene_dictionary_q = gene_dictionary_q.reset_index(drop = True)
    elif species == 'both':
        tf_h = ['Homo sapiens' in x and 'Mus musculus' in x for x in gene_dictionary['species']]
        gene_dictionary_q = gene_dictionary[tf_h].copy()
        gene_dictionary_q = gene_dictionary_q.reset_index(drop = True)
    else:
        tf_h = ['Homo sapiens' in x or 'Mus musculus' in x for x in gene_dictionary['species']]
        gene_dictionary_q = gene_dictionary[tf_h].copy()
        gene_dictionary_q = gene_dictionary_q.reset_index(drop = True)
    
    
    return gene_dictionary_q


#ref_gene
def download_ref(path = _path_tmp):
    
    print('\n')
    print('REF-GENOME downloading...')
   
    urllib.request.urlretrieve('https://github.com/jkubis96/JRefGen/raw/main/MixedGenomeAnnotation/gene_dictionary_jbio.json', path + '/gene_dictionary_jbio.json')
   
    with open(path + '/gene_dictionary_jbio.json', 'r') as json_file:
        gene_dictionary = (json.load(json_file))
        
    os.remove(path + '/gene_dictionary_jbio.json')

    return gene_dictionary
    
#ref_gene-RNA-SEQ
def download_rns_seq(path = _path_tmp):
    
    print('\n')
    print('RNA-SEQ data downloading...')
   
    urllib.request.urlretrieve('https://github.com/jkubis96/JRefGen/raw/main/RNA_SEQ/human_tissue_expression_HPA.json', path + '/human_tissue_expression_HPA.json')
    urllib.request.urlretrieve('https://github.com/jkubis96/JRefGen/raw/main/RNA_SEQ/human_tissue_expression_RNA_total_tissue.json', path + '/human_tissue_expression_RNA_total_tissue.json')
    urllib.request.urlretrieve('https://github.com/jkubis96/JRefGen/raw/main/RNA_SEQ/human_tissue_expression_fetal_development_circular.json', path + '/human_tissue_expression_fetal_development_circular.json')
    urllib.request.urlretrieve('https://github.com/jkubis96/JRefGen/raw/main/RNA_SEQ/human_tissue_expression_illumina_bodyMap2.json', path + '/human_tissue_expression_illumina_bodyMap2.json')
    
    with open(path + '/human_tissue_expression_HPA.json', 'r') as json_file:
        human_tissue_expression_HPA = json.load(json_file)
        
    os.remove(path + '/human_tissue_expression_HPA.json')
    
    
    with open(path + '/human_tissue_expression_RNA_total_tissue.json', 'r') as json_file:
        human_tissue_expression_RNA_total_tissue = json.load(json_file)
        
    os.remove(path + '/human_tissue_expression_RNA_total_tissue.json')
    
    
    with open(path + '/human_tissue_expression_fetal_development_circular.json', 'r') as json_file:
        human_tissue_expression_fetal_development_circular = json.load(json_file)
        
    os.remove(path + '/human_tissue_expression_fetal_development_circular.json')
    
    
    with open(path + '/human_tissue_expression_illumina_bodyMap2.json', 'r') as json_file:
        human_tissue_expression_illumina_bodyMap2 = json.load(json_file)
        
    os.remove(path + '/human_tissue_expression_illumina_bodyMap2.json')

    rna_seq_list = {'human_tissue_expression_HPA':human_tissue_expression_HPA, 
                    'human_tissue_expression_RNA_total_tissue':human_tissue_expression_RNA_total_tissue, 
                    'human_tissue_expression_fetal_development_circular':human_tissue_expression_fetal_development_circular, 
                    'human_tissue_expression_illumina_bodyMap2':human_tissue_expression_illumina_bodyMap2}
    
    return rna_seq_list





#IntAct_download
def download_IntAct(path = _path_tmp):
    
    """
    This function retrieves data from the IntAct database and saves them under the given path

    Args:
       path (str)- path to save
       
    Returns:
       file: IntAct database file saved in the given path
       
    """
    
    print('\n')
    print('IntAct data downloading...')

    
    if not os.path.exists(path + '/tmp'):
        try:
            os.makedirs(path + '/tmp')
            print(f"Directory '{path}' created successfully.")
        except OSError as e:
            print(f"Error creating the directory: {e}")
    else:
        print('\n')
        print(f"Directory '{path}' already exists.")


    
    #Affinomics - Interactions curated for the Affinomics consortium
    urllib.request.urlretrieve('https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Affinomics.zip', path + '/tmp/Affinomics.zip')
    
    with zipfile.ZipFile(path + '/tmp/Affinomics.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Affinomics.zip')

    #Alzheimers - Interaction dataset based on proteins with an association to Alzheimer disease
    urllib.request.urlretrieve('https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Alzheimers.zip', path + '/tmp/Alzheimers.zip')
    
    with zipfile.ZipFile(path + '/tmp/Alzheimers.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Alzheimers.zip')
    
    
    #BioCreative - Critical Assessment of Information Extraction systems in Biology
    urllib.request.urlretrieve('https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/BioCreative.zip', path + '/tmp/BioCreative.zip')
    
    with zipfile.ZipFile(path + '/tmp/BioCreative.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/BioCreative.zip')
    
 
    #Cancer - Interactions investigated in the context of cancer
    urllib.request.urlretrieve('https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Cancer.zip', path + '/tmp/Cancer.zip')
    
    with zipfile.ZipFile(path + '/tmp/Cancer.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Cancer.zip')
    
    
    #Cardiac - Interactions involving cardiac related proteins
    urllib.request.urlretrieve('https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Cardiac.zip', path + '/tmp/Cardiac.zip')
    
    with zipfile.ZipFile(path + '/tmp/Cardiac.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Cardiac.zip')
    
    
    #Chromatin - Epigenetic interactions resulting in chromatin modulation
    urllib.request.urlretrieve('https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Chromatin.zip', path + '/tmp/Chromatin.zip')
    
    with zipfile.ZipFile(path + '/tmp/Chromatin.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Chromatin.zip')
    
    
    #Coronavirus - Interactions investigated in the context of Coronavirus
    urllib.request.urlretrieve('https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Coronavirus.zip', path + '/tmp/Coronavirus.zip')
    
    with zipfile.ZipFile(path + '/tmp/Coronavirus.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Coronavirus.zip')
    
    
    #Cyanobacteria - Interaction dataset based on Cyanobacteria proteins and related species
    urllib.request.urlretrieve('https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Cyanobacteria.zip', path + '/tmp/Cyanobacteria.zip')
    
    with zipfile.ZipFile(path + '/tmp/Cyanobacteria.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Cyanobacteria.zip')
    
    
    #Diabetes - Interactions investigated in the context of Diabetes
    urllib.request.urlretrieve('https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Diabetes.zip', path + '/tmp/Diabetes.zip')
    
    with zipfile.ZipFile(path + '/tmp/Diabetes.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Diabetes.zip')
    
    
    #Huntington's - Publications describing interactions involved in Huntington's disease
    urllib.request.urlretrieve("https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Huntington's.zip", path + '/tmp/Huntington.zip')
    
    with zipfile.ZipFile(path + '/tmp/Huntington.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Huntington.zip')
    
    
    #IBD - Inflammatory bowel disease
    urllib.request.urlretrieve("https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/IBD.zip", path + '/tmp/IBD.zip')
    
    with zipfile.ZipFile(path + '/tmp/IBD.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/IBD.zip')
    
    
    #Neurodegeneration - Publications depicting interactions involved in neurodegenerative disease
    urllib.request.urlretrieve("https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Neurodegeneration.zip", path + '/tmp/Neurodegeneration.zip')
    
    with zipfile.ZipFile(path + '/tmp/Neurodegeneration.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Neurodegeneration.zip')
    
    
    #Parkinsons - Interactions investigated in the context of Parkinsons disease
    urllib.request.urlretrieve("https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Parkinsons.zip", path + '/tmp/Parkinsons.zip')
    
    with zipfile.ZipFile(path + '/tmp/Parkinsons.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Parkinsons.zip')
    
    
    #Rare Diseases - Interactions investigated in the context of Rare genetic diseases
    urllib.request.urlretrieve("https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Rare_diseases.zip", path + '/tmp/Rare_diseases.zip')
    
    with zipfile.ZipFile(path + '/tmp/Rare_diseases.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Rare_diseases.zip')
    
    
    #Ulcerative colitis - Interactions of proteins identified as having a link to ulcerative colitis
    urllib.request.urlretrieve("https://ftp.ebi.ac.uk/pub/databases/intact/current/psi30/datasets/Ulcerative_colitis.zip", path + '/tmp/Ulcerative_colitis.zip')
    
    with zipfile.ZipFile(path + '/tmp/Ulcerative_colitis.zip', 'r') as zip_ref:
        zip_ref.extractall(path + '/tmp')
                
    os.remove(path + '/tmp/Ulcerative_colitis.zip')
    
    



def XML_to_dict(path = _path_tmp):
    mutual_dcit = pd.DataFrame()
    for source in tqdm(os.listdir(path + '/tmp')):
        print('\n\n' + source)
        for int_id in tqdm(os.listdir(path + '/tmp/' + source)):
            if 'negative' not in int_id:
                with open(path + '/tmp/' + source + '/' + int_id, 'r',  encoding='utf-8') as file:
                    xml_content = file.read()
    
                
                
                xml = BeautifulSoup(xml_content, "xml")
                
                del xml_content

                tmp = xml.find_all('interactor')
    
    
    
                interactors = {
                    'id': [],
                    'gene_name': [],
                    'full_name': [],
                    'species': [],
                    # 'interactor_type_full_name': [],
    
                }
    
                for des in tmp:
                    ids = int(des.get('id'))
                    fullName = des.find('fullName').text
                    gene_name = des.find('alias', attrs={'type': 'gene name'})
                    if gene_name:
                        gene_name = gene_name.text.strip()
                    else:
                        gene_name = des.find('primaryRef')
                        if gene_name:
                            gene_n = re.sub('.*id="', '', str(gene_name))
                            gene_n = re.sub('".*', '', str(gene_n))
                            gene_name = 'Non-gene product [' + gene_n + ']'
    
                    tmp2 = des.find_all('organism')
                    species = []
                    for des2 in tmp2:
                        species.append(des2.find('fullName').text)
    
                    # Append the data to the list
                    interactors['id'].append(ids)
                    interactors['gene_name'].append(gene_name)
                    interactors['full_name'].append(fullName)
                    interactors['species'].append(species[0])
    
                # 'interactorType'
                # 'interaction'
                del tmp
                del tmp2
                tmp = xml.find_all('interaction')
    
                interactions = {'gene_interaction': [],
                                'gene_1_id': [],
                                'gene_2_id': [],
                                'experiment_id': [],
                                'interaction_type': [],
                                'gene_1_biological_role': [],
                                'gene_2_biological_role': [],
                                'gene_1_experimental_role': [],
                                'gene_2_experimental_role': []
    
    
                                }
    
                for des in tmp:
                    interaction_name = des.find('shortLabel').text
    
                    interactor_refs = des.find_all('interactorRef')
                    interactor_refs = [int(ref.text) for ref in interactor_refs]
    
                    biological_roles = des.find_all('biologicalRole')
                    biological_roles = [
                        role.find('fullName').text for role in biological_roles]
    
                    experimentalRole = des.find_all('experimentalRole')
                    experimentalRole = [
                        role.find('fullName').text for role in experimentalRole]
    
                    interactionType = des.find_all('interactionType')
                    interactionType = [
                        role.find('fullName').text for role in interactionType]
    
                    experimentList = des.find_all('experimentList')
                    experimentList = [int(role.find('experimentRef').text)
                                      for role in experimentList]
    
                    if len(interactor_refs) == 2:
                        interactions['gene_interaction'].append(interaction_name)
                        interactions['gene_1_id'].append(interactor_refs[0])
                        interactions['gene_2_id'].append(interactor_refs[1])
                        interactions['experiment_id'].append(experimentList[0])
                        interactions['interaction_type'].append(interactionType[0])
                        interactions['gene_1_biological_role'].append(
                            biological_roles[0])
                        interactions['gene_2_biological_role'].append(
                            biological_roles[1])
                        interactions['gene_1_experimental_role'].append(
                            experimentalRole[0])
                        interactions['gene_2_experimental_role'].append(
                            experimentalRole[1])
                    elif len(interactor_refs) == 1 and biological_roles[0] == 'putative self':
                        interactions['gene_interaction'].append(interaction_name)
                        interactions['gene_1_id'].append(interactor_refs[0])
                        interactions['gene_2_id'].append(interactor_refs[0])
                        interactions['experiment_id'].append(experimentList[0])
                        interactions['interaction_type'].append(interactionType[0])
                        interactions['gene_1_biological_role'].append(
                            biological_roles[0])
                        interactions['gene_2_biological_role'].append(
                            biological_roles[0])
                        interactions['gene_1_experimental_role'].append(
                            experimentalRole[0])
                        interactions['gene_2_experimental_role'].append(
                            experimentalRole[0])
                  
    
                # 'experimentDescription'
                del tmp, interaction_name, interactor_refs, biological_roles, experimentalRole, experimentList
             
                
                tmp = xml.find_all('experimentDescription')
    
                del xml
                experimental = {
                    'ExperimentID': [],
                    'PublicationTitle': [],
                    'Journal': [],
                    'PublicationYear': [],
                    'AuthorList': [],
                    'Model': [],
                    'Detection_method':[]
                    
                }
                
                for des in tmp:
                    try:
                        experiment_id = int(des.get('id'))
                    except:
                        experiment_id = None
                    
                    try:
                        publication_title = des.find('attribute', attrs={'name': 'publication title'}).text
                    except:
                        publication_title = None
    
                    try:
                        journal = des.find('attribute', attrs={'name': 'journal'}).text
                    except:
                        journal = None
    
                    try:
                        publication_year = des.find('attribute', attrs={'name': 'publication year'}).text
                    except:
                        publication_year = None
                        
                    try:
                        author_list = des.find('attribute', attrs={'name': 'author-list'}).text
                    except:
                        author_list = None
                        
                    
                    try:
                        models = des.find_all('hostOrganismList')
                        model = []
                        for model_t in models:
                            models2 = model_t.find_all('fullName')
                            for t in models2:
                                model.append(t.text)
                                
                        model = ', '.join(model)
    
                    except:
                        models = None
                        
                    try:
                        detection_method = des.find_all('interactionDetectionMethod')
                        detection = []
                        for dect in detection_method:
                            dect2 = dect.find_all('fullName')
                            for t in dect2:
                                detection.append(t.text)
                                
                        detection = ', '.join(detection)
    
                    except:
                        detection = None
                        

                
                    # Append the data to the list
                   
                    experimental['ExperimentID'].append(experiment_id),
                    experimental['PublicationTitle'].append(publication_title),
                    experimental['Journal'].append(journal),
                    experimental['PublicationYear'].append(publication_year),
                    experimental['AuthorList'].append(author_list),
                    experimental['Detection_method'].append(detection)
                    experimental['Model'].append(model)
                    del journal, detection, detection_method, models, model, publication_year, author_list, experiment_id, publication_title
    
          
                
                del tmp
    
  
                experimental = pd.DataFrame(experimental)   
                interactions = pd.DataFrame(interactions)   
                interactors = pd.DataFrame(interactors)   
                interactors_g1 = interactors.copy()
                interactors_g1.columns = interactors_g1.columns + '_1'
                interactors_g2 = interactors.copy()
                interactors_g2.columns = interactors_g2.columns + '_2'
                
                del interactors
    

                interactions = pd.merge(interactions, experimental, left_on = 'experiment_id' , right_on = 'ExperimentID' , how = 'left')
                interactions = pd.merge(interactions, interactors_g1, left_on = 'gene_1_id' , right_on = 'id_1' , how = 'left')
                try:
                    interactions = pd.merge(interactions, interactors_g2, left_on = 'gene_2_id' , right_on = 'id_2' , how = 'left')
                    interactions = interactions.drop(['gene_1_id', 'gene_2_id', 'experiment_id', 'ExperimentID', 'id_1', 'id_2'], axis = 1)

                except:
                    interactions = interactions.drop(['gene_1_id', 'gene_2_id', 'experiment_id', 'ExperimentID', 'id_1'], axis = 1)
                    None
    
                
                interactions['source'] = str(source)
                interactions['set_id'] = str(int_id)
                
            
    
                mutual_dcit = pd.concat([mutual_dcit, pd.DataFrame(interactions)])
                
                
                
                
    mutual_dcit = mutual_dcit.reset_index(drop = True)
    
    print('Repairing the data...')
    for i, e in enumerate(mutual_dcit['gene_interaction']):
        if mutual_dcit['gene_name_1'][i].upper() not in e.upper() or mutual_dcit['gene_name_2'][i].upper() not in e.upper():
            mutual_dcit = mutual_dcit.drop(i)
            
    mutual_dcit = mutual_dcit.reset_index(drop = True)
              
    mutual_dcit = mutual_dcit.to_dict(orient = 'list')
    
    try:       
        shutil.rmtree(path + '/tmp/')
        os.makedirs(path + '/tmp')
        print(f"The temporary file was removed successfully")
    except OSError as e:
        print(f"Error deleting the file: {e}")
        
    return mutual_dcit


def download_IntAct_data(path = _path_tmp):
    
    """
    This function retrieves data from the IntAct database 

    Args:
       path (str)- path to save
       
    Returns:
       dict: IntAct database file in dictionary format
       
    """
    
    try:
    
        download_IntAct(path)
        IntAct = XML_to_dict(path)
        
        return IntAct
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")


#DISEASE_download
def download_diseases(path = _path_tmp):
    
    """
    This function retrieves data from the DISEASES database 

    Args:
       path (str)- path to save
       
    Returns:
       dict: DISEASES database file in dictionary format
       
    """
    
    print('\n')
    print('DISEASES data downloading...')


    try:
        urllib.request.urlretrieve('https://download.jensenlab.org/human_disease_knowledge_filtered.tsv', path + '/knowledge_disease.tsv')
        urllib.request.urlretrieve('https://download.jensenlab.org/human_disease_textmining_filtered.tsv', path + '/mining_disease.tsv')
        urllib.request.urlretrieve('https://download.jensenlab.org/human_disease_experiments_filtered.tsv', path + '/experiments_disease.tsv')
            
            
        knowledge = pd.read_csv(path + '/knowledge_disease.tsv', sep = '\t', header= None)
        experiment = pd.read_csv(path + '/experiments_disease.tsv', sep = '\t', header= None)
        mining = pd.read_csv(path + '/mining_disease.tsv', sep = '\t', header= None)
        
        disease = pd.concat([knowledge, experiment, mining])
        
        disease = disease[[0,1,3]]
        
        disease.columns = ['gene', 'protein', 'disease']
        
        disease = disease.drop_duplicates()
    
        dictionary = disease.to_dict(orient = 'list')
        
        
        try:
            os.remove(path + '/knowledge_disease.tsv')
            os.remove(path + '/experiments_disease.tsv')
            os.remove(path + '/mining_disease.tsv')
            print(f"The temporary file was removed successfully")
        except OSError as e:
            print(f"Error deleting the file: {e}")
        
        return dictionary
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




#VIRUSES_download
def download_viral_deiseases(path = _path_tmp):
    
    """
    This function retrieves data from the ViMIC database 

    Args:
       path (str)- path to save
       
    Returns:
       dict: ViMIC database file in dictionary format
       
    """
    
    print('\n')
    print('ViMIC data downloading...')

    try:
        
        urllib.request.urlretrieve('http://bmtongji.cn/ViMIC/downloaddata/targetgene/Target_gene.xlsx', path + '/viruse_disease.xlsx')
    
        viruses = pd.read_excel(path + '/viruse_disease.xlsx')
    
        dictionary = viruses.to_dict(orient = 'list')
        
        try:
            os.remove(path + '/viruse_disease.xlsx')
            print(f"The temporary file was removed successfully")
        except OSError as e:
            print(f"Error deleting the file: {e}")
        
        return dictionary
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



    
#HPA download
def download_HPA(path = _path_tmp):
    
    """
    This function retrieves data from the Human Protein Atlas database 

    Args:
       path (str)- path to save
       
    Returns:
       dict: Human Protein Atlas database file in dictionary format
       
    """
    
    print('\n')
    print('HPA data downloading...')

    
    try:
        urllib.request.urlretrieve('https://www.proteinatlas.org/download/proteinatlas.tsv.zip', path + '/proteinatlas.tsv.zip')
        
        with zipfile.ZipFile(path + '/proteinatlas.tsv.zip', 'r') as zip_ref:
            with zip_ref.open('proteinatlas.tsv', 'r') as f_in:
                with open(path + '/proteinatlas.tsv', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
        HPA = pd.read_csv(path + '/proteinatlas.tsv', sep= '\t')
        
        
        try:
            os.remove(path + '/proteinatlas.tsv.zip')
            os.remove(path + '/proteinatlas.tsv')

    
            print(f"The temporary file was removed successfully")
        except OSError as e:
            print(f"Error deleting the file: {e}")
    
        dictionary = HPA.to_dict(orient = 'list')
        
        return dictionary
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



 
#STRING
def download_string(path = _path_tmp):
    
    """
    This function retrieves data from the STRING database 

    Args:
       path (str)- path to save
       
    Returns:
       dict: STRING database file in dictionary format
       
    """
    
    print('\n')
    print('STRING data downloading...')

    try:
        urllib.request.urlretrieve('https://stringdb-static.org/download/protein.links.full.v11.5/9606.protein.links.full.v11.5.txt.gz', path + '/inter_human.txt.gz')
        urllib.request.urlretrieve('https://stringdb-static.org/download/protein.info.v11.5/9606.protein.info.v11.5.txt.gz', path + '/info_human.txt.gz')
        
        with gzip.open(path + '/inter_human.txt.gz', 'r') as f_in:
            with open(path + '/inter_human.txt', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        with gzip.open(path + '/info_human.txt.gz', 'r') as f_in:
            with open(path + '/info_human.txt', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
                
        urllib.request.urlretrieve('https://stringdb-static.org/download/protein.links.full.v11.5/10090.protein.links.full.v11.5.txt.gz', path + '/inter_mouse.txt.gz')
        urllib.request.urlretrieve('https://stringdb-static.org/download/protein.info.v11.5/10090.protein.info.v11.5.txt.gz', path + '/info_mouse.txt.gz')
        
        with gzip.open(path + '/inter_mouse.txt.gz', 'r') as f_in:
            with open(path + '/inter_mouse.txt', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        with gzip.open(path + '/info_mouse.txt.gz', 'r') as f_in:
            with open(path + '/info_mouse.txt', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
           
            
            
        string_hh = pd.read_csv(path + '/inter_human.txt', sep = ' ')
        
        string_hh = string_hh[['protein1', 'protein2', 'combined_score']]
        
        string_ih = pd.read_csv(path + '/info_human.txt', sep = '\t')
        
        
        string_hm = pd.read_csv(path + '/inter_mouse.txt', sep = ' ')
        
        string_hm = string_hm[['protein1', 'protein2', 'combined_score']]
    
        string_im = pd.read_csv(path + '/info_mouse.txt', sep = '\t')
        
    
        dictionary = {'human_ppi':string_hh.to_dict(orient = 'list'), 'human_annotations':string_ih.to_dict(orient = 'list'), 'mouse_ppi':string_hm.to_dict(orient = 'list'), 'mouse_annotations':string_im.to_dict(orient = 'list')}
        
        try:
            os.remove(path + '/inter_human.txt')
            os.remove(path + '/info_human.txt')
            os.remove(path + '/inter_mouse.txt')
            os.remove(path + '/info_mouse.txt')
            os.remove(path + '/inter_human.txt.gz')
            os.remove(path + '/info_human.txt.gz')
            os.remove(path + '/inter_mouse.txt.gz')
            os.remove(path + '/info_mouse.txt.gz')
    
            print(f"The temporary file was removed successfully")
        except OSError as e:
            print(f"Error deleting the file: {e}")
            
        return dictionary
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def scpecies_concatenate(string):
    mouse = pd.DataFrame(string['mouse_annotations'])
    mouse['preferred_name'] = [x.upper() for x in mouse['preferred_name']]
    human = pd.DataFrame(string['human_annotations'])
    human['preferred_name'] = [x.upper() for x in human['preferred_name']]
    human['species'] = 'human'
    mouse['species'] = 'mouse'

    
    mouse_ppi = pd.DataFrame(string['mouse_ppi'])
    name_mapping = dict(zip(mouse['#string_protein_id'], mouse['preferred_name']))
    mouse_ppi['protein1'] = mouse_ppi['protein1'].map(name_mapping)
    mouse_ppi['protein2'] = mouse_ppi['protein2'].map(name_mapping)
    mouse_ppi['species'] = 'mouse'

    human_ppi = pd.DataFrame(string['human_ppi'])
    name_mapping = dict(zip(human['#string_protein_id'], human['preferred_name']))
    human_ppi['protein1'] = human_ppi['protein1'].map(name_mapping)
    human_ppi['protein2'] = human_ppi['protein2'].map(name_mapping)
    human_ppi['species'] = 'human'
    
    ppi = pd.concat([mouse_ppi, human_ppi])
    
    del human_ppi, mouse_ppi
    
    metadata = pd.concat([human, mouse])
    metadata = metadata.groupby('preferred_name').agg({'species': list, 'annotation': list, 'protein_size': list}).reset_index()
    
    ppi = ppi.to_dict(orient = 'list')
    metadata = metadata.to_dict(orient = 'list')

    dictionary = {'ppi':ppi, 'metadata':metadata} 
    

    return dictionary


    
  
#KEGG


#################################################################################

def download_kegg(path = _path_tmp):
    
    
    """
    This function retrieves data from the KEGG database 

    Args:
       path (str)- path to save
       
    Returns:
       dict: KEGG database file in dictionary format
       
    """
    
    print('\n')
    print('KEGG data downloading...')

    
    try:
    
        urllib.request.urlretrieve('https://www.kegg.jp/kegg-bin/download_htext?htext=ko00001.keg&format=json&filedir=', path + '/kegg.json')
        
        with open(path + '/kegg.json') as j:
            kegg = json.load(j)
        
        
        first = []
        second = []
        third = []
        fourth = []
        
        
        for n, inx in enumerate(tqdm(kegg['children'])):
            for i, inx in enumerate(kegg['children'][n]['children']):
                for j, inx in enumerate(kegg['children'][n]['children'][i]['children']):
                    try:
                        kegg['children'][n]['children'][i]['children'][j]['children'] 
                    except:
                        break
                    for k, inx in enumerate(kegg['children'][n]['children'][i]['children'][j]['children']):
                        try:
                            kegg['children'][n]['children'][i]['children'][j]['children'][k]
                        except:
                            break
                       
                        first.append(re.sub('\d+' ,'',kegg['children'][n]['name'])[1:len(re.sub('\d+' ,'',kegg['children'][n]['name']))])
                        second.append(re.sub('\d+' ,'',kegg['children'][n]['children'][i]['name'])[1:len(re.sub('\d+' ,'',kegg['children'][n]['children'][i]['name']))])
                        third.append(re.sub(' \[.*' ,'',str(kegg['children'][n]['children'][i]['children'][j]['name'])[6:len(str(kegg['children'][n]['children'][i]['children'][j]['name']))]))
                        fourth.append(str(kegg['children'][n]['children'][i]['children'][j]['children'][k]['name'])[8:len(str(kegg['children'][n]['children'][i]['children'][j]['children'][k]['name']))])
        
        df = pd.DataFrame({'1st':first, '2nd':second, '3rd':third, '4th':fourth}).reset_index(drop = True)
        df = df.drop_duplicates().reset_index(drop = True)
        df['gene'] = [re.sub(';.*' ,'',y).split(",") for y in df['4th']]
        df['name'] = [re.sub(re.sub(';.*' ,'',y) + '; ' ,'',df['4th'][n]) for n, y in enumerate(df['4th'])]
        df = df.drop(['4th'],  axis = 1)
        df = df.reset_index(drop = True)
    
        df = df.to_dict(orient = 'list')
        
        
        try:
            os.remove(path + '/kegg.json')
         
    
            print(f"The temporary file was removed successfully")
        except OSError as e:
            print(f"Error deleting the file: {e}")
        
        
        return df
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")
    
  


#REACTOME




def download_reactome(path = _path_tmp):
    
    """
    This function retrieves data from the REACTOME database 

    Args:
       path (str)- path to save
       
    Returns:
       dict: REACTOME database file in dictionary format
       
    """
    
    print('\n')
    print('REACTOME data downloading...')

    
    try:
        
        urllib.request.urlretrieve('https://reactome.org/download/current/ReactomePathways.gmt.zip', path + '/reactome.zip')
        
        
        
        with zipfile.ZipFile(path + '/reactome.zip', 'r') as zip_ref:
            # Extract all the files to the destination directory
            zip_ref.extractall(path + '/reactome')
            
        
        
        with open(path + '/reactome/ReactomePathways.gmt', 'r') as file:
            # Iterate through the lines of the file
            path_name = []
            path_id = []
            gen = []
            for line in file:
                tmp = line.strip().split("\t")
                for li in range(2,len(tmp)):
                    path_name.append(tmp[0])
                    path_id.append(tmp[1])
                    gen.append(tmp[li])
                
        df = pd.DataFrame({'path_name':path_name, 'path_id':path_id, 'gene':gen})
        
        df = df.groupby('gene').agg({'path_name': list, 'path_id': list}).reset_index()
        
        
    
        connections = pd.read_csv('https://reactome.org/download/current/ReactomePathwaysRelation.txt', header=None, sep=  '\t')
        connections = connections.groupby(0).agg({1:list}).reset_index()
        connections.columns = ['parent', 'children']
        
        connections = connections.to_dict(orient = 'list')  
        
        df = df.reset_index(drop = True)
        
        df = df.to_dict(orient = 'list')    
    
        dictionary = {'metadata':df, 'connections':connections}
        
        try:
            os.remove(path + '/reactome/ReactomePathways.gmt')
            os.remove(path + '/reactome.zip')
            shutil.rmtree(path + '/reactome/')
    
            print(f"The temporary file was removed successfully")
        except OSError as e:
            print(f"Error deleting the file: {e}")
    
        
        return dictionary 
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def download_go_connections():
  
    response = requests.get('http://purl.obolibrary.org/obo/go.obo') 
    
    GO_id = []
    name = []
    name_space = []
    synonym = []
    definition = []
    children = []
    obsolete = []
    alternative_id = []
    list_of_lines = []
    intersection = []
    relationship = []
    part_of = []
    
    l = 0
    if response.status_code == 200:
        
        # Iterate through each line in the response content
        
        term = []
        for n,line in enumerate(response.iter_lines()):
            line = line.decode("utf-8")
            list_of_lines.append(line)
            
            
            if '[Term]' in str(line):
                term.append(n)
                
      
        for en, j in enumerate(range(len(term))):
            tmp_child = []
            tmp_syn = []
            tmp_alt = []
            tmp_int = []
            tmp_relationship = []
            tmp_part_of = []
            
            if j <= len(term)-2:
                tmp = list_of_lines[term[j]:term[j+1]]
                for l in tmp:
                    if 'id: GO' in l and '_id:' not in l:
                        GO_id.append(re.sub('id: ', '', l))
                    if 'name:' in l:
                        name.append(re.sub('name: ', '', l))
                    if 'is_obsolete:' in l:
                        obsolete.append(bool(re.sub('is_obsolete: ', '', l)))
                    if 'namespace:' in l:
                        name_space.append(re.sub('namespace: ', '', l))
                    if 'def:' in l:
                        definition.append(re.sub('\[.*', '', re.sub('"', '', re.sub('def: ', '', l))))
                    if 'synonym:' in l:
                        tmp_syn.append(re.sub('\[.*', '', re.sub('"', '', re.sub('synonym: ', '', l))))
                    if 'is_a:' in l:
                        tmp_child.append(re.sub('\[.*', '', re.sub('"', '', re.sub('is_a: ', '', l))))
                    if 'alt_id:' in l:
                        tmp_alt.append(re.sub('\[.*', '', re.sub('"', '', re.sub('alt_id: ', '', l))))
                    if 'intersection_of:' in l:
                        tmp_int.append(re.sub('"', '', re.sub('intersection_of: ', '', l)))
                    if 'relationship:' in l:
                        tmp_relationship.append(re.sub('', '', re.sub('"', '', re.sub('relationship: ', '', l))))
                    if 'part_of:' in l:
                        tmp_part_of.append(re.sub('', '', re.sub('"', '', re.sub('part_of: ', '', l))))
                  
                if len(tmp_syn) == 0:
                    synonym.append(None)
                else:
                    synonym.append(tmp_syn)
                if len(tmp_alt) == 0:
                    alternative_id.append(None)
                else:
                    alternative_id.append(tmp_alt)
                if len(tmp_int) == 0:
                    intersection.append(None)
                else:
                    intersection.append(tmp_int)
                if len(tmp_relationship) == 0:
                    relationship.append(None)
                else:
                    relationship.append(tmp_relationship)
                if len(tmp_part_of) == 0:
                    part_of.append(None)
                else:
                    part_of.append(tmp_part_of)
                if len(tmp_child) == 0:
                    children.append(None)
                else:
                    children.append(tmp_child)
        
                if len(GO_id) < en+1:
                    GO_id.append(None)
                if len(name) < en+1:
                    name.append(None)
                if len(obsolete) < en+1:
                    obsolete.append(False)
                if len(name_space) < en+1:
                    name_space.append(None)
                if len(definition) < en+1:
                    definition.append(None)
    
                
    df = {'GO_id':GO_id, 'name':name, 'name_space':name_space, 'synonym':synonym, 'definition':definition, 'definition':definition,
          'alternative_id':alternative_id, 'children':children, 'intersection':intersection, 'relationship':relationship, 'part_of':part_of, 'obsolete':obsolete}
    
    df = pd.DataFrame(df)
    
    df['is_a_ids'] = None
    df['part_of_ids'] = None
    df['has_part_ids'] = None
    df['regulates_ids'] = None
    df['negatively_regulates_ids'] = None
    df['positively_regulates_ids'] = None
    df['is_a_des'] = None
    df['part_of_des'] = None
    df['regulates_des'] = None
    df['negatively_regulates_des'] = None
    df['positively_regulates_des'] = None
    df['has_part_des'] = None
    
    ####
    for n ,inter in enumerate(tqdm(df['intersection'])):
        if inter != None:
            if 'regulates' in df['intersection'][n][1] and 'negatively_regulates' not in df['intersection'][n][1] and 'positively_regulates' not in df['intersection'][n][1]:
                #
                if df['regulates_ids'][n] == None:
                    df['regulates_ids'][n] = [re.sub(' !.*' , '', df['intersection'][n][0])]
                else:
                    df['regulates_ids'][n] = df['regulates_ids'][n] + [re.sub(' !.*' , '', df['intersection'][n][0])]
                
                if df['regulates_des'][n] == None:
                    df['regulates_des'][n] = [re.sub('.*! ' , '', df['intersection'][n][0])]
                else:
                    df['regulates_des'][n] = df['regulates_des'][n] + [re.sub('.*! ' , '', df['intersection'][n][0])]
                  
                #
                if df['regulates_ids'][n] == None:
                    df['regulates_ids'][n] = [re.sub('regulates ' , '', re.sub(' !.*' , '', df['intersection'][n][1]))]
                else:
                    df['regulates_ids'][n] = df['regulates_ids'][n] + [re.sub('regulates ' , '', re.sub(' !.*' , '', df['intersection'][n][1]))]
                
                if df['regulates_des'][n] == None:
                    df['regulates_des'][n] = [re.sub('.*! ' , '', df['intersection'][n][1])]
                else:
                    df['regulates_des'][n] = df['regulates_des'][n] + [re.sub('.*! ' , '', df['intersection'][n][1])]
                    
            elif 'positively_regulates' in df['intersection'][n][1] and 'negatively_regulates' not in df['intersection'][n][1]:
                #
                if df['positively_regulates_ids'][n] == None:
                    df['positively_regulates_ids'][n] = [re.sub(' !.*' , '', df['intersection'][n][0])]
                else:
                    df['positively_regulates_ids'][n] = df['positively_regulates_ids'][n] + [re.sub(' !.*' , '', df['intersection'][n][0])]
                
                if df['positively_regulates_des'][n] == None:
                    df['positively_regulates_des'][n] = [re.sub('.*! ' , '', df['intersection'][n][0])]
                else:
                    df['positively_regulates_des'][n] = df['positively_regulates_des'][n] + [re.sub('.*! ' , '', df['intersection'][n][0])]
                  
                #
                if df['positively_regulates_ids'][n] == None:
                    df['positively_regulates_ids'][n] = [re.sub('positively_regulates ' , '', re.sub(' !.*' , '', df['intersection'][n][1]))]
                else:
                    df['positively_regulates_ids'][n] = df['positively_regulates_ids'][n] + [re.sub('positively_regulates ' , '', re.sub(' !.*' , '', df['intersection'][n][1]))]
                
                if df['positively_regulates_des'][n] == None:
                    df['positively_regulates_des'][n] = [re.sub('.*! ' , '', df['intersection'][n][1])]
                else:
                    df['positively_regulates_des'][n] = df['positively_regulates_des'][n] + [re.sub('.*! ' , '', df['intersection'][n][1])]
            
            elif 'negatively_regulates' in df['intersection'][n][1] and 'positively_regulates' not in df['intersection'][n][1]:
                #
                if df['negatively_regulates_ids'][n] == None:
                    df['negatively_regulates_ids'][n] = [re.sub(' !.*' , '', df['intersection'][n][0])]
                else:
                    df['negatively_regulates_ids'][n] = df['negatively_regulates_ids'][n] + [re.sub(' !.*' , '', df['intersection'][n][0])]
                
                if df['negatively_regulates_des'][n] == None:
                    df['negatively_regulates_des'][n] = [re.sub('.*! ' , '', df['intersection'][n][0])]
                else:
                    df['negatively_regulates_des'][n] = df['negatively_regulates_des'][n] + [re.sub('.*! ' , '', df['intersection'][n][0])]
                  
                #
                if df['negatively_regulates_ids'][n] == None:
                    df['negatively_regulates_ids'][n] = [re.sub('negatively_regulates ' , '', re.sub(' !.*' , '', df['intersection'][n][1]))]
                else:
                    df['negatively_regulates_ids'][n] = df['negatively_regulates_ids'][n] + [re.sub('negatively_regulates ' , '', re.sub(' !.*' , '', df['intersection'][n][1]))]
                
                if df['negatively_regulates_des'][n] == None:
                    df['negatively_regulates_des'][n] = [re.sub('.*! ' , '', df['intersection'][n][1])]
                else:
                    df['negatively_regulates_des'][n] = df['negatively_regulates_des'][n] + [re.sub('.*! ' , '', df['intersection'][n][1])]
        
        if df['relationship'][n] != None:
            for f in df['relationship'][n]:
                if 'regulates' in f and 'negatively_regulates' not in f and 'positively_regulates' not in f:
                    #
                    if df['regulates_ids'][n] == None:
                        df['regulates_ids'][n] = [re.sub('regulates ' , '', re.sub(' !.*' , '', f))]
                    else:
                        df['regulates_ids'][n] = df['regulates_ids'][n] + [re.sub('regulates ' , '', re.sub(' !.*' , '', f))]
                    
                    if df['regulates_des'][n] == None:
                        df['regulates_des'][n] = [re.sub('.*! ' , '', f)]
                    else:
                        df['regulates_des'][n] = df['regulates_des'][n] + [re.sub('.*! ' , '', f)]
                      
                elif 'positively_regulates' in f and 'negatively_regulates' not in f:
                    #
                    if df['positively_regulates_ids'][n] == None:
                        df['positively_regulates_ids'][n] = [re.sub('positively_regulates ' , '', re.sub(' !.*' , '', f))]
                    else:
                        df['positively_regulates_ids'][n] = df['positively_regulates_ids'][n] + [re.sub('positively_regulates ' , '', re.sub(' !.*' , '', f))]
                    
                    if df['positively_regulates_des'][n] == None:
                        df['positively_regulates_des'][n] = [re.sub('.*! ' , '', f)]
                    else:
                        df['positively_regulates_des'][n] = df['positively_regulates_des'][n] + [re.sub('.*! ' , '', f)]
                      
                
                
                elif 'negatively_regulates' in f and 'positively_regulates' not in f:
                    #
                    if df['negatively_regulates_ids'][n] == None:
                        df['negatively_regulates_ids'][n] = [re.sub('negatively_regulates ' , '', re.sub(' !.*' , '', f))]
                    else:
                        df['negatively_regulates_ids'][n] = df['negatively_regulates_ids'][n] + [re.sub('negatively_regulates ' , '', re.sub(' !.*' , '', f))]
                    
                    if df['negatively_regulates_des'][n] == None:
                        df['negatively_regulates_des'][n] = [re.sub('.*! ' , '', f)]
                    else:
                        df['negatively_regulates_des'][n] = df['negatively_regulates_des'][n] + [re.sub('.*! ' , '', f)]
                        
                
                elif 'has_part' in f:
                    #
                    if df['has_part_ids'][n] == None:
                        df['has_part_ids'][n] = [re.sub('has_part ' , '', re.sub(' !.*' , '', f))]
                    else:
                        df['has_part_ids'][n] = df['has_part_ids'][n] + [re.sub('has_part ' , '', re.sub(' !.*' , '', f))]
                    
                    if df['has_part_des'][n] == None:
                        df['has_part_des'][n] = [re.sub('.*! ' , '', f)]
                    else:
                        df['has_part_des'][n] = df['has_part_des'][n] + [re.sub('.*! ' , '', f)]
                        
                elif 'part_of' in f:
                    #
                    if df['part_of_ids'][n] == None:
                        df['part_of_ids'][n] = [re.sub('part_of ' , '', re.sub(' !.*' , '', f))]
                    else:
                        df['part_of_ids'][n] = df['part_of_ids'][n] + [re.sub('part_of ' , '', re.sub(' !.*' , '', f))]
                    
                    if df['part_of_des'][n] == None:
                        df['part_of_des'][n] = [re.sub('.*! ' , '', f)]
                    else:
                        df['part_of_des'][n] = df['part_of_des'][n] + [re.sub('.*! ' , '', f)]
        
        if df['children'][n] != None:
            for f in df['children'][n]:
                #
                if df['is_a_ids'][n] == None:
                    df['is_a_ids'][n] = [re.sub(' !.*' , '', f)]
                else:
                    df['is_a_ids'][n] = df['is_a_ids'][n] + [re.sub(' !.*' , '', f)]
                
                if df['is_a_des'][n] == None:
                    df['is_a_des'][n] = [re.sub('.*! ' , '', f)]
                else:
                    df['is_a_des'][n] = df['is_a_des'][n] + [re.sub('.*! ' , '', f)]
           
    
    df = df.drop(['children', 'relationship', 'intersection'], axis = 1)
    df = df.to_dict(orient = 'list')

    
    return df





def download_go_annotations(path = _path_tmp):
#### GO annotation mouse & human
    urllib.request.urlretrieve('http://geneontology.org/gene-associations/goa_human.gaf.gz', path + '/goa_human.gaf.gz')
    
    
    
    
    with gzip.open(path + '/goa_human.gaf.gz', 'r') as f_in:
        with open(path + '/goa_human.gaf', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        
    df2 = pd.read_csv(path + '/goa_human.gaf', sep = '\t', skiprows = 41, header=None)
    df2 = df2[[0,1,2,3,4,5,6,9,10,11,12]]
    df2.columns = ['source', 'source_id', 'gene_name', 'connection', 'GO_id', 'ref', 'confidence_code', 'description', 'protein_name', 'function', 'tax_id']
    df2['species'] = 'Homo sapiens'
    
    ####
    urllib.request.urlretrieve('http://current.geneontology.org/annotations/mgi.gaf.gz', path + '/mgi.gaf.gz')
    
    
    
    with gzip.open(path + '/mgi.gaf.gz', 'r') as f_in:
        with open(path + '/mgi.gaf', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        
    df3 = pd.read_csv(path + '/mgi.gaf', sep = '\t', skiprows = 36, header=None)
    df3 = df3[[0,1,2,3,4,5,6,9,10,11,12]]
    df3.columns = ['source', 'source_id', 'gene_name', 'connection', 'GO_id', 'ref', 'confidence_code', 'description', 'protein_name', 'function', 'tax_id']
    df3['species'] = 'Mus musculus'
    
    annotation = pd.concat([df2, df3])
    
    
    annotation = annotation[(annotation['gene_name'] == annotation['gene_name'])]
    
    annotation = annotation.to_dict(orient = 'list')
    
    
    try:
        os.remove(path + '/mgi.gaf.gz')
        os.remove(path + '/mgi.gaf')
        os.remove(path + '/goa_human.gaf.gz')
        os.remove(path + '/goa_human.gaf')

        print(f"The temporary file was removed successfully")
    except OSError as e:
        print(f"Error deleting the file: {e}")
    
    return annotation

    

def download_go_term(path = _path_tmp):
    
    """
    This function retrieves data from the GO-TERM database 

    Args:
       path (str)- path to save
       
    Returns:
       dict: GO-TERM database file in dictionary format
       
    """
    
    print('\n')
    print('GO-TERM data downloading...')

    try:
        
        go_annotation = download_go_annotations(path)
        go_term = download_go_connections()     
        
        dictionary = {'metadata':go_annotation, 'connections':go_term}
        
        
        return dictionary
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")


def update_downloading(path = _path_inside, path_in_use = _path_in_inside, password = None):
            
    print('\n')
    print('Data downloading starting...')
    print('Data are downloaded from many sources so this process can last several minutes...')

    
    ref = download_ref(path)
    
    
    with open(path + '/gene_dictionary_jbio.json', 'w') as json_file:
        json.dump(ref, json_file)
        
    del ref
    
    #RNA_seq data
    rs_seq = download_rns_seq(path_in_use)
    

    for r in rs_seq.keys():
        print(r)
    
        with open(path_in_use + '/' + str(r) + '.json', 'w') as json_file:
            json.dump(rs_seq[r], json_file)
    
        
    del rs_seq
    
    download_IntAct(path)
    
    
    
    IntAct = XML_to_dict(path)
    
    with open(path + '/IntAct_jbio.json', 'w') as json_file:
        json.dump(IntAct, json_file)
    
    del IntAct
    
    
    diseases = download_diseases(path)
    
    with open(path + '/diseases_jbio.json', 'w') as json_file:
        json.dump(diseases, json_file)
        
    del diseases
    
    
    viral_diseases = download_viral_deiseases(path)
    
    with open(path + '/viral_diseases_jbio.json', 'w') as json_file:
        json.dump(viral_diseases, json_file)
        
    del viral_diseases
           
    
    
    HPA = download_HPA(path)
    
    with open(path + '/HPA_jbio.json', 'w') as json_file:
        json.dump(HPA, json_file)
        
    del HPA
       
    
    string = download_string(path)
    
    
    string_dict = scpecies_concatenate(string)
    
    
    
    with open(path + '/string_jbio.json', 'w') as json_file:
        json.dump(string_dict, json_file)
       
    del string, string_dict
    
      
    kegg = download_kegg(path)
    
    
    
    with open(path + '/kegg_jbio.json', 'w') as json_file:
        json.dump(kegg, json_file)
        
    del kegg
    
    
    reactome = download_reactome(path)
    
    
    
    with open(path + '/reactome_jbio.json', 'w') as json_file:
        json.dump(reactome, json_file)
    
    del reactome
    
    
    
    go_term = download_go_term(path)
    
    with open(path + '/goterm_jbio.json', 'w') as json_file:
        json.dump(go_term, json_file)
        
    del go_term
    
    current_date = datetime.today().date()
    current_date = current_date.strftime("%d-%m-%Y")
    
    text = 'The last GOPa update was done on ' + str(current_date)

    if password.upper() == 'JBS':
        text = text + '\nThe GOPa data version authorized by JBS(R)'
        text = text + '\nThe GOPa data version: GOPa-' + re.sub('-','/',current_date)
    else:
        text = text + '\nThe GOPa data version unauthorized'
        text = text + '\nThe GOPa data version: User_custom-' + re.sub('-','/',current_date)

        
    
    # Open the file in write mode and save the string to it
    with open(path + '/update.dat', "w") as file:
        file.write(text)
    
    
    print('\n')
    print('Data download has finished...')
        



def check_last_update(path = _path_inside):
    
    """
    This function checks the last udate of data used in this library

    Args:
       path (str)- path to library (for library use)
       
    Returns:
       date: Date of last update
       
    """
    
    with open(path + '/update.dat', "r") as file:
        print('\n')
        print(file.read())


#Database mapping to gene dictionary functions

    
def reactome_to_gene_dict(reactome_jbio, gene_dictionary):
    reactome = pd.DataFrame(reactome_jbio['metadata'])
    reactome['id'] = reactome.index
    reactome['id'] = [int(x) for x in reactome['id'] if x == x]
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    reactome['gene'] = [x.upper() for x in reactome['gene']]
    
    gene_dictionary = pd.merge(gene_dictionary, reactome[['gene', 'id']], left_on = 'gene_name', right_on= 'gene',  how='left')
    
    undefined = list(reactome['gene'][~reactome['gene'].isin(gene_dictionary['gene'])])
    
    
    
    synonymes = []
    for x in tqdm(gene_dictionary['synonymes']):
        if x == x:
            synonymes = synonymes + x
    
    synonymes = [y.upper() for y in synonymes]
    
    unknow = []
    for syn in tqdm(undefined):
        if syn.upper() in synonymes:
            for i in gene_dictionary.index:
                if gene_dictionary['synonymes'][i] == gene_dictionary['synonymes'][i] and syn.upper() in gene_dictionary['synonymes'][i] and gene_dictionary['id'][i] != gene_dictionary['id'][i]:
                    # print(reactome_jbio['id'][reactome_jbio['gene'] == syn])
                    gene_dictionary['id'][i] = int(reactome['id'][reactome['gene'] == syn.upper()])
        else:
            unknow.append(syn)
    
    gene_dictionary = gene_dictionary.rename(columns={"id": "id_reactome"})
    gene_dictionary = gene_dictionary.drop('gene', axis = 1)
    gene_dictionary = gene_dictionary.to_dict(orient = 'list')
    reactome = reactome.to_dict(orient = 'list')
    reactome_jbio['metadata'] = reactome
    
    return reactome_jbio, gene_dictionary



    
#HPA to dict

def HPA_to_gene_dict(HPA_jbio, gene_dictionary):
    
    HPA_jbio = pd.DataFrame(HPA_jbio)
        
    HPA_jbio['Gene'] = [re.sub(' ', '', x.upper()) for x in HPA_jbio['Gene']]
    
    HPA_jbio = HPA_jbio.drop_duplicates()
    
    jdci = pd.DataFrame({'names':list(set(HPA_jbio['Gene'])), 'id':range(len(list(set(HPA_jbio['Gene']))))})

    jdci['id'] = [int(x) for x in jdci['id']]
    
    HPA_jbio = pd.merge(HPA_jbio, jdci[['names', 'id']], left_on = 'Gene', right_on= 'names',  how='left')
        
    HPA_jbio = HPA_jbio.drop('names', axis = 1)
    
    HPA_jbio_dict = HPA_jbio.copy()
    
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    
    synonymes = []
    for x in tqdm(gene_dictionary['synonymes']):
        if x == x:
            synonymes = synonymes + x
    
    synonymes = [y.upper() for y in synonymes]
    
    
    gene_dictionary = pd.merge(gene_dictionary, HPA_jbio[['Gene', 'id']].drop_duplicates(), left_on = 'gene_name', right_on='Gene',  how='left')

    
        
    
    HPA_jbio = HPA_jbio[~HPA_jbio['id'].isin(HPA_jbio['id'])]
    HPA_jbio = HPA_jbio[(HPA_jbio['Gene'].isin(synonymes))]
    
    
    gene_dictionary2 = gene_dictionary[['synonymes', 'dictionary_id']].explode('synonymes').reset_index(drop=True)
    
    
    gene_dictionary2 = pd.merge(gene_dictionary2, HPA_jbio[['Gene', 'id']].drop_duplicates(), left_on = 'synonymes', right_on= 'Gene',  how='left')
    

    gene_dictionary2 = gene_dictionary2.dropna(subset=['id'])
    gene_dictionary2 = gene_dictionary2[['id', 'dictionary_id']]
    gene_dictionary2 = gene_dictionary2.drop_duplicates().reset_index(drop = True)


    for i, n in enumerate(gene_dictionary2['dictionary_id']):
        if gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]] != gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]]:
            gene_dictionary['id'][gene_dictionary['dictionary_id'] == n] = int(gene_dictionary2['id'][i])
            
            
    gene_dictionary = gene_dictionary.rename(columns={"id": "id_HPA"})
    
    gene_dictionary = gene_dictionary.drop('Gene', axis = 1)


    
    gene_dictionary = gene_dictionary.to_dict(orient = 'list')
    
    HPA_jbio_dict = HPA_jbio_dict.to_dict(orient = 'list')
    
    return HPA_jbio_dict, gene_dictionary


    
#DISEASES

def diseases_to_gene_dict(disease_dict, gene_dictionary):
    
    disease_dict = pd.DataFrame(disease_dict)
    
    disease_dict['gene'] = [re.sub(' ', '', x.upper()) for x in disease_dict['gene']]
    
    disease_dict = disease_dict.drop_duplicates()
    
    jdci = pd.DataFrame({'names':list(set(disease_dict['gene'])), 'id':range(len(list(set(disease_dict['gene']))))})

    jdci['id'] = [int(x) for x in jdci['id']]
    
    disease_dict = pd.merge(disease_dict, jdci[['names', 'id']], left_on = 'gene', right_on= 'names',  how='left')
        
    disease_dict = disease_dict.drop('names', axis = 1)
    
    disease_dict_jbio = disease_dict.copy()
    
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    
    synonymes = []
    for x in tqdm(gene_dictionary['synonymes']):
        if x == x:
            synonymes = synonymes + x
    
    synonymes = [y.upper() for y in synonymes]
    
    
    gene_dictionary = pd.merge(gene_dictionary, disease_dict[['gene', 'id']].drop_duplicates(), left_on = 'gene_name', right_on='gene',  how='left')
    gene_dictionary = pd.merge(gene_dictionary, disease_dict[['protein', 'id']].drop_duplicates(), left_on = 'gene_name', right_on='protein',  how='left')

    for inx in tqdm(gene_dictionary.index):
        if gene_dictionary['id_x'][inx] != gene_dictionary['id_x'][inx] and gene_dictionary['id_y'][inx] == gene_dictionary['id_y'][inx]:
            gene_dictionary['id_x'][inx] = gene_dictionary['id_y'][inx]
    
    gene_dictionary = gene_dictionary.drop('id_y', axis = 1)
    
    
    disease_dict = disease_dict[~disease_dict['id'].isin(gene_dictionary['id_x'])]
    disease_dict = disease_dict[(disease_dict['gene'].isin(synonymes)) | (disease_dict['protein'].isin(synonymes))]
    
    
    gene_dictionary2 = gene_dictionary[['synonymes', 'dictionary_id']].explode('synonymes').reset_index(drop=True)
    
    
    gene_dictionary2 = pd.merge(gene_dictionary2, disease_dict[['gene', 'id']].drop_duplicates(), left_on = 'synonymes', right_on= 'gene',  how='left')
    gene_dictionary2 = pd.merge(gene_dictionary2, disease_dict[['protein', 'id']].drop_duplicates(), left_on = 'synonymes', right_on= 'protein',  how='left')

    for inx in tqdm(gene_dictionary.index):
        if gene_dictionary2['id_x'][inx] != gene_dictionary2['id_x'][inx] and gene_dictionary2['id_y'][inx] == gene_dictionary2['id_y'][inx]:
            gene_dictionary2['id_x'][inx] = gene_dictionary2['id_y'][inx]

    gene_dictionary2 = gene_dictionary2.dropna(subset=['id_x'])
    gene_dictionary2 = gene_dictionary2[['id_x', 'dictionary_id']]
    gene_dictionary2 = gene_dictionary2.drop_duplicates().reset_index(drop = True)


    for i, n in enumerate(gene_dictionary2['dictionary_id']):
        if gene_dictionary['id_x'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]] != gene_dictionary['id_x'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]]:
            gene_dictionary['id_x'][gene_dictionary['dictionary_id'] == n] = int(gene_dictionary2['id_x'][i])
            
            
    gene_dictionary = gene_dictionary.rename(columns={"id_x": "id_diseases"})
    
    gene_dictionary = gene_dictionary.drop('gene', axis = 1)
    gene_dictionary = gene_dictionary.drop('protein', axis = 1)


    
    gene_dictionary = gene_dictionary.to_dict(orient = 'list')
    
    disease_dict_jbio = disease_dict_jbio.to_dict(orient = 'list')
    
    return disease_dict_jbio, gene_dictionary



#VIRAL-DISEASES
    
def viral_diseases_to_gene_dict(viral_dict, gene_dictionary):
    
    viral_dict = pd.DataFrame(viral_dict)
    
    viral_dict['Target_gene'] = [re.sub(' ', '', x.upper()) for x in viral_dict['Target_gene']]
    
    viral_dict = viral_dict.drop_duplicates()
    
    jdci = pd.DataFrame({'names':list(set(viral_dict['Target_gene'])), 'id':range(len(list(set(viral_dict['Target_gene']))))})

    jdci['id'] = [int(x) for x in jdci['id']]
    
    viral_dict = pd.merge(viral_dict, jdci[['names', 'id']], left_on = 'Target_gene', right_on= 'names',  how='left')
        
    viral_dict = viral_dict.drop('names', axis = 1)
    
    viral_dict_jbio = viral_dict.copy()
    
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    
    synonymes = []
    for x in tqdm(gene_dictionary['synonymes']):
        if x == x:
            synonymes = synonymes + x
    
    synonymes = [y.upper() for y in synonymes]
    
    
    gene_dictionary = pd.merge(gene_dictionary, viral_dict[['Target_gene', 'id']].drop_duplicates(), left_on = 'gene_name', right_on='Target_gene',  how='left')
   
    
    viral_dict = viral_dict[~viral_dict['id'].isin(gene_dictionary['id'])]
    viral_dict = viral_dict[(viral_dict['Target_gene'].isin(synonymes))]
    
    
    gene_dictionary2 = gene_dictionary[['synonymes', 'dictionary_id']].explode('synonymes').reset_index(drop=True)
    
    
    gene_dictionary2 = pd.merge(gene_dictionary2, viral_dict[['Target_gene', 'id']].drop_duplicates(), left_on = 'synonymes', right_on= 'Target_gene',  how='left')


    gene_dictionary2 = gene_dictionary2.dropna(subset=['id'])
    gene_dictionary2 = gene_dictionary2[['id', 'dictionary_id']]
    gene_dictionary2 = gene_dictionary2.drop_duplicates().reset_index(drop = True)


    for i, n in enumerate(gene_dictionary2['dictionary_id']):
        if gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]] != gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]]:
            gene_dictionary['id'][gene_dictionary['dictionary_id'] == n] = int(gene_dictionary2['id'][i])
            
            
    gene_dictionary = gene_dictionary.rename(columns={"id": "id_viral_diseases"})
    
    gene_dictionary = gene_dictionary.drop('Target_gene', axis = 1)


    
    gene_dictionary = gene_dictionary.to_dict(orient = 'list')
    viral_dict_jbio = viral_dict_jbio[['Target_gene', 'virus', 'group', 'id']]
    viral_dict_jbio.columns = ['gen_name', 'virus_disease', 'group', 'id']
    viral_dict_jbio['virus_disease'] =  viral_dict_jbio['virus_disease'] + ' related interaction'  
    viral_dict_jbio = viral_dict_jbio.to_dict(orient = 'list')
    
    return viral_dict_jbio, gene_dictionary




#KEGG   

def kegg_to_gene_dict(kegg_jbio, gene_dictionary):
    
    kegg_jbio = pd.DataFrame(kegg_jbio)
    
    kegg_jbio = kegg_jbio.explode('gene').reset_index(drop=True)
    
    kegg_jbio['gene'] = [re.sub(' ', '', x.upper()) for x in kegg_jbio['gene']]
    
    kegg_jbio = kegg_jbio.drop_duplicates()
    
    kegg_jbio = kegg_jbio.reset_index(drop = True)
    
    #rm non human entitis
    list_to_rm_KEGG = ['Viral', 'Mycobacterium', 'HIV-1', 'virus', 'fly', 'plant', 'yeast', 'animal', 'Caulobacter' , 'Vibrio cholerae', 'Pseudomonas aeruginosa', 'Escherichia coli', 'worm' ,'antenna proteins']

    bacteria_names_latin = [
        "Escherichia coli",
        "Staphylococcus aureus",
        "Bacillus subtilis",
        "Mycobacterium tuberculosis",
        "Helicobacter pylori",
        "Clostridium difficile",
        "Salmonella enterica",
        "Lactobacillus acidophilus",
        "Pseudomonas aeruginosa",
        "Listeria monocytogenes",
        "Vibrio cholerae",
        "Mycoplasma pneumoniae",
        "Treponema pallidum",
        "Chlamydia trachomatis",
        "Borrelia burgdorferi",
        "Yersinia pestis",
        "Neisseria meningitidis",
        "Enterococcus faecalis",
        "Streptococcus pyogenes",
        "Campylobacter jejuni",
        "Corynebacterium diphtheriae",
        "Methanobrevibacter smithii",
        "Acetobacter aceti",
        "Lactococcus lactis",
        "Bacteroides fragilis",
        "Rhizobium leguminosarum",
        "Agrobacterium tumefaciens",
        "Helicobacter pylori",
        "Clostridium botulinum",
        "Bacillus anthracis",
        "Borrelia burgdorferi",
        "Chlamydia pneumoniae",
        "Legionella pneumophila",
        "Cyanobacterium Prochlorococcus",
        "Thermus aquaticus",
        "Deinococcus radiodurans",
        "Streptomyces coelicolor",
        "Shigella flexneri",
        "Chlorobium tepidum",
        "Lactobacillus casei",
        "Micrococcus luteus",
        "Spirochaeta africana",
        "Geobacter sulfurreducens",
        "Thermotoga maritima",
        "Verrucomicrobium spinosum",
        "Prevotella bryantii",
        "Desulfovibrio vulgaris",
        "Halobacterium salinarum",
        "Rickettsia prowazekii",
        "Leptospira interrogans",
        "Francisella tularensis",
        "Bacteroides thetaiotaomicron",
        "Streptococcus mutans",
        "Thermotoga neapolitana",
        "Deinococcus geothermalis",
        "Rhodopseudomonas palustris",
        "Bifidobacterium longum",
        "Candidatus Carsonella ruddii",
        "Magnetospirillum magneticum",
        "Desulforudis audaxviator",
        "Myxococcus xanthus",
        "Methanosarcina barkeri",
        "Propionibacterium acnes",
        "Nitrosomonas europaea",
        "Clostridium acetobutylicum",
        "Buchnera aphidicola",
        "Ruminococcus albus",
        "Chlorobaculum tepidum",
        "Aquifex aeolicus",
        "Shewanella oneidensis",
        "Lactococcus garvieae",
        "Mycoplasma genitalium",
        "Mycoplasma gallisepticum",
        "Thermus thermophilus",
        "Stenotrophomonas maltophilia",
        "Anaplasma marginale",
        "Treponema denticola",
        "Leptospira biflexa",
        "Vibrio fischeri",
        "Caulobacter crescentus",
        "Bartonella henselae",
        "Brucella abortus",
        "Rickettsia rickettsii",
        "Flavobacterium johnsoniae",
        "Candidatus Sulcia muelleri",
        "Escherichia coli O157:H7",
        "Aeromonas hydrophila",
        "Pseudomonas fluorescens",
        "Caulobacter vibrioides",
        "Xanthomonas campestris",
        "Legionella longbeachae",
        "Bordetella pertussis",
        "Coxiella burnetii",
        "Nitrosomonas eutropha",
        "Bacillus cereus",
        "Bifidobacterium adolescentis",
        "Brucella melitensis",
        "Yersinia enterocolitica",
        "Verrucomicrobium sp.",
        "Geobacter metallireducens",
        "Desulfovibrio desulfuricans",
        "Salmonella typhi",
        "Pseudomonas putida",
        "Chlamydia suis",
        "Rickettsia typhi",
        "Leptospira borgpetersenii",
        "Rhodopirellula baltica"
       
    ]


    yeast_and_candida_names_latin = [
        "Saccharomyces cerevisiae",
        "Candida albicans",
        "Saccharomyces pastorianus",
        "Cryptococcus neoformans",
        "Kluyveromyces lactis",
        "Debaryomyces hansenii",
        "Pichia pastoris",
        "Candida glabrata",
        "Candida krusei",
        "Yarrowia lipolytica",
        "Candida parapsilosis",
        "Saccharomyces bayanus",
        "Saccharomyces mikatae",
        "Saccharomyces paradoxus",
        "Candida tropicalis",
        "Pichia stipitis",
        "Saccharomyces kudriavzevii",
        "Candida utilis",
        "Candida lusitaniae",
        "Pichia methanolica",
        "Candida guilliermondii",
        "Candida auris",
        "Candida rugosa",
        "Candida kefyr",
        "Schizosaccharomyces pombe",
        "Candida zeylanoides",
        "Zygosaccharomyces bailii",
        "Hanseniaspora uvarum",
        "Issatchenkia orientalis",
        "Brettanomyces bruxellensis",
        "Pichia guilliermondii",
        "Candida famata",
        "Candida milleri",
        "Candida pelliculosa",
        "Candida vini",
        "Candida viswanathii",
        "Candida intermedia",
        "Saccharomycodes ludwigii",
        "Lodderomyces elongisporus",
        "Kluyveromyces marxianus",
        "Candida stellimalicola",
        "Metschnikowia pulcherrima",
        "Pichia jadinii",
        "Candida haemulonii",
        "Wickerhamomyces anomalus",
        "Candida silvicultrix",
        "Kazachstania africana",
        "Candida sake",
        "Candida dubliniensis",
        "Debaryomyces fabryi",
        "Candida maltosa",
        "Candida orthopsilosis",
        "Yamadazyma terventina",
        "Kazachstania servazzii",
        "Pichia membranifaciens",
        "Pichia kudriavzevii",
        "Lipomyces starkeyi",
        "Candida castellii",
        "Candida diddensiae",
        "Candida norvegensis",
        "Candida wickerhamii",
        "Candida fermentati",
        "Candida solani",
        "Candida pararugosa",
        "Candida rancensis",
        "Candida maris",
        "Candida incommunis",
        "Saccharomyces exiguus",
        "Candida oleophila",
        "Candida sorbophila",
        "Candida ethanolica",
        "Candida valdiviana",
        "Candida californica",
        "Candida membranifaciens",
        "Kazachstania heterogenica",
        "Candida azyma",
        "Candida blattae",
        "Candida athensensis",
        "Candida nivariensis",
        "Kazachstania unispora",
        "Candida pseudohaemulonii",
        "Candida jeffriesii",
        "Candida silvae",
        "Candida orthofermentans",
        "Candida sojae",
        "Kazachstania exigua",
        "Candida tsuchiyae",
        "Candida macedoniensis",
        "Candida lactis",
        "Candida cellae",
        "Candida deserticola",
        "Candida viswanathii",
        "Candida friedrichii",
        "Candida crustulenta",
        "Candida musae",
        "Candida robnettiae",
        "Candida dutilhii",
        "Candida langeronii",
        "Candida monacensis",
        "Candida vaughaniae",
        "Candida spearei",
        "Candida margaritae",
        "Candida lundensis",
        "Candida catenulata",
        "Candida sojana",
        "Candida meyerae",
        "Candida thailandica",
        "Candida idiomarina",
        "Candida vartiovaarae",
        "Candida hanlinii",
        "Candida colliculosa",
        "Candida liburnica",
        "Candida holmii",
        "Candida americana",
        "Candida ranongensis",
        "Candida slooffiae",
        "Candida margarethae",
        "Candida taylorii",
        "Candida kluyveri",
        "Candida castellanii",
        "Candida europaea",
        "Candida floricola",
        "Candida lambica",
        "Candida surugaensis",
        "Candida oregonensis",
        "Candida hetfieldiae",
        "Candida wissei",
        "Candida dairensis",
        "Candida friedrichii",
        "Candida psychrophila",
        "Candida mesorugosa",
        "Candida stellimalicola",
        "Candida heliconiae",
        "Candida fukuyamaensis",
        "Candida odintsovae",
        "Candida phangngensis",
        "Candida peltatoides",
        "Candida tsukubaensis",
        "Candida olei",
        "Candida temperata",
        "Candida coipomoensis",
        "Candida ishiwadae",
        "Candida subtropicalis",
        "Candida scottii",
        "Candida cruzei",
        "Candida aaseri",
        "Candida aquaticus",
        "Candida diogoi",
        "Candida fluvialitis",
        "Candida heliconiae",
        "Candida maltosa",
        "Candida monilioides",
        "Candida oleophila",
        "Candida parapsilosis" 
    ]

    list_to_rm_KEGG = list_to_rm_KEGG + bacteria_names_latin + yeast_and_candida_names_latin

    inx_list = []
    for inx in tqdm(kegg_jbio.index):
        for i in list_to_rm_KEGG:
            if i in str(kegg_jbio['3rd'][inx]) and 'Human Diseases' not in str(kegg_jbio['1st'][inx]):
                inx_list.append(inx)
                break

    kegg_jbio = kegg_jbio.drop(index=inx_list)
    
    kegg_jbio = kegg_jbio[~kegg_jbio['3rd'].isin(['Function unknown', 'General function prediction only', 'Unclassified viral proteins', 'Others', 'Enzymes with EC numbers', 'Domain-containing proteins not elsewhere classified'])]
    
    kegg_jbio = kegg_jbio.reset_index(drop = True)
    
    jdci = pd.DataFrame({'names':list(set(kegg_jbio['gene'])), 'id':range(len(list(set(kegg_jbio['gene']))))})

    jdci['id'] = [int(x) for x in jdci['id']]
    
    kegg_jbio = pd.merge(kegg_jbio, jdci[['names', 'id']], left_on = 'gene', right_on= 'names',  how='left')
        
    kegg_jbio = kegg_jbio.drop('names', axis = 1)
    
    kegg_jbio_dict = kegg_jbio.copy()
    
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    
    synonymes = []
    for x in tqdm(gene_dictionary['synonymes']):
        if x == x:
            synonymes = synonymes + x
    
    synonymes = [y.upper() for y in synonymes]
    
    
    gene_dictionary = pd.merge(gene_dictionary, kegg_jbio[['gene', 'id']].drop_duplicates(), left_on = 'gene_name', right_on= 'gene',  how='left')
    
    
    kegg_jbio = kegg_jbio[~kegg_jbio['id'].isin(gene_dictionary['id'])]
    kegg_jbio = kegg_jbio[kegg_jbio['gene'].isin(synonymes)]
    
    
    gene_dictionary2 = gene_dictionary[['synonymes', 'dictionary_id']].explode('synonymes').reset_index(drop=True)
    
    
    gene_dictionary2 = pd.merge(gene_dictionary2, kegg_jbio[['gene', 'id']].drop_duplicates(), left_on = 'synonymes', right_on= 'gene',  how='left')
    gene_dictionary2 = gene_dictionary2.dropna(subset=['id'])
    gene_dictionary2 = gene_dictionary2[['id', 'dictionary_id']]
    gene_dictionary2 = gene_dictionary2.drop_duplicates().reset_index(drop = True)


    for i, n in enumerate(gene_dictionary2['dictionary_id']):
        if gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]] != gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]]:
            gene_dictionary['id'][gene_dictionary['dictionary_id'] == n] = int(gene_dictionary2['id'][i])
            
            
    gene_dictionary = gene_dictionary.rename(columns={"id": "id_kegg"})
    
    gene_dictionary = gene_dictionary.drop('gene', axis = 1)
    
    gene_dictionary = gene_dictionary.to_dict(orient = 'list')
    
    kegg_jbio_dict = kegg_jbio_dict.to_dict(orient = 'list')
    
    return kegg_jbio_dict, gene_dictionary



##GO-TERM

def go_to_gene_dict(go_term_jbio, gene_dictionary):
    
    go_term = pd.DataFrame(go_term_jbio['metadata'])
    
    go_term['gene_name'] = [x.upper() for x in go_term['gene_name']]
    jdci = pd.DataFrame({'names':list(set(go_term['gene_name'])), 'id':range(len(list(set(go_term['gene_name']))))})
    
    jdci['id'] = [int(x) for x in jdci['id']]

    go_term = go_term.drop_duplicates()
    

    go_term = pd.merge(go_term, jdci[['names', 'id']], left_on = 'gene_name', right_on= 'names',  how='left')
        
    go_term = go_term.drop('names', axis = 1)
    
    go_term_dict = go_term.copy()
    
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    
    synonymes = []
    for x in tqdm(gene_dictionary['synonymes']):
        if x == x:
            synonymes = synonymes + x
    
    synonymes = [y.upper() for y in synonymes]
    
    
    gene_dictionary = pd.merge(gene_dictionary, go_term[['gene_name', 'id']].drop_duplicates(), on = 'gene_name',  how='left')
    
    
    go_term = go_term[~go_term['id'].isin(gene_dictionary['id'])]
    go_term = go_term[go_term['gene_name'].isin(synonymes)]
    
    
    gene_dictionary2 = gene_dictionary[['synonymes', 'dictionary_id']].explode('synonymes').reset_index(drop=True)
    
    
    gene_dictionary2 = pd.merge(gene_dictionary2, go_term[['gene_name', 'id']].drop_duplicates(), left_on = 'synonymes', right_on= 'gene_name',  how='left')
    gene_dictionary2 = gene_dictionary2.dropna(subset=['id'])
    gene_dictionary2 = gene_dictionary2[['id', 'dictionary_id']]
    gene_dictionary2 = gene_dictionary2.drop_duplicates().reset_index(drop = True)


    for i, n in enumerate(gene_dictionary2['dictionary_id']):
        if gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]] != gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]]:
            gene_dictionary['id'][gene_dictionary['dictionary_id'] == n] = int(gene_dictionary2['id'][i])
            
            
    gene_dictionary = gene_dictionary.rename(columns={"id": "id_go"})
        
    gene_dictionary = gene_dictionary.to_dict(orient = 'list')
    
    go_term_dict = go_term_dict.to_dict(orient = 'list')
    
    go_term_jbio['metadata'] = go_term_dict
    
    return go_term_jbio, gene_dictionary



#INTACT

def intact_to_gene_dict(IntAct_dict, gene_dictionary):
    
    IntAct_dict = pd.DataFrame(IntAct_dict)
    IntAct_dict = IntAct_dict.reset_index(drop = True)
    IntAct_dict = IntAct_dict[IntAct_dict['species_1'].isin(['Homo sapiens', 'Mus musculus'])]
    IntAct_dict = IntAct_dict[IntAct_dict['species_2'].isin(['Homo sapiens', 'Mus musculus'])]

    
    IntAct_dict['gene_name_1'] = [x.upper() for x in IntAct_dict['gene_name_1']]
    IntAct_dict['gene_name_2'] = [x.upper() for x in IntAct_dict['gene_name_2']]

    genes = list(IntAct_dict['gene_name_1']) + list(IntAct_dict['gene_name_2'])
    
    jdci = pd.DataFrame({'names':list(set(genes)), 'id':range(len(list(set(genes))))})
    
    jdci['id'] = [int(x) for x in jdci['id']]


    IntAct_dict = pd.merge(IntAct_dict, jdci[['names', 'id']], left_on = 'gene_name_1', right_on= 'names',  how='left')
    IntAct_dict = IntAct_dict.drop('names', axis = 1)
    IntAct_dict = IntAct_dict.rename(columns={'id':'id_1'})


    IntAct_dict = pd.merge(IntAct_dict, jdci[['names', 'id']], left_on = 'gene_name_2', right_on= 'names',  how='left')
    IntAct_dict = IntAct_dict.drop('names', axis = 1)
    IntAct_dict = IntAct_dict.rename(columns={'id':'id_2'})


    
    
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    
    synonymes = []
    for x in tqdm(gene_dictionary['synonymes']):
        if x == x:
            synonymes = synonymes + x
    
    synonymes = [y.upper() for y in synonymes]

    
    gene_dictionary = pd.merge(gene_dictionary, jdci.drop_duplicates(), left_on = 'gene_name', right_on= 'names',  how='left')
    
    
    jdci = jdci[~jdci['id'].isin(gene_dictionary['id'])]
    jdci = jdci[jdci['names'].isin(synonymes)]
    
    
    gene_dictionary2 = gene_dictionary[['synonymes', 'dictionary_id']].explode('synonymes').reset_index(drop=True)
    
    
    gene_dictionary2 = pd.merge(gene_dictionary2, jdci.drop_duplicates(), left_on = 'synonymes', right_on= 'names',  how='left')
    gene_dictionary2 = gene_dictionary2.dropna(subset=['id'])
    gene_dictionary2 = gene_dictionary2[['id', 'dictionary_id']]
    gene_dictionary2 = gene_dictionary2.drop_duplicates().reset_index(drop = True)


    for i, n in enumerate(gene_dictionary2['dictionary_id']):
        if gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]] != gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]]:
            gene_dictionary['id'][gene_dictionary['dictionary_id'] == n] = int(gene_dictionary2['id'][i])
            
            
    gene_dictionary = gene_dictionary.rename(columns={"id": "id_IntAct"})
    
    gene_dictionary = gene_dictionary.drop('names', axis = 1)
        
    gene_dictionary = gene_dictionary.to_dict(orient = 'list')

    
    IntAct_dict = IntAct_dict.to_dict(orient = 'list')
    
    return IntAct_dict, gene_dictionary



#STRING

def string_to_gene_dict(string_dict, gene_dictionary):
    
    string_annotations = pd.DataFrame(string_dict['metadata'])
    string_annotations = string_annotations.reset_index(drop = True)
    
    string_annotations['preferred_name'] = [x.upper() for x in string_annotations['preferred_name']]
    jdci = pd.DataFrame({'names':list(set(string_annotations['preferred_name'])), 'id':range(len(list(set(string_annotations['preferred_name']))))})
    
    jdci['id'] = [int(x) for x in jdci['id']]


    string_annotations = pd.merge(string_annotations, jdci[['names', 'id']], left_on = 'preferred_name', right_on= 'names',  how='left')
        
    string_annotations = string_annotations.drop('names', axis = 1)
    
    string_annotations_dict = string_annotations.to_dict(orient = 'list')
    
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    
    synonymes = []
    for x in tqdm(gene_dictionary['synonymes']):
        if x == x:
            synonymes = synonymes + x
    
    synonymes = [y.upper() for y in synonymes]
    
    
    gene_dictionary = pd.merge(gene_dictionary, string_annotations[['preferred_name', 'id']].drop_duplicates(), left_on = 'gene_name', right_on= 'preferred_name',  how='left')
    
    
    string_annotations = string_annotations[~string_annotations['id'].isin(gene_dictionary['id'])]
    string_annotations = string_annotations[string_annotations['preferred_name'].isin(synonymes)]
    
    
    gene_dictionary2 = gene_dictionary[['synonymes', 'dictionary_id']].explode('synonymes').reset_index(drop=True)
    
    
    gene_dictionary2 = pd.merge(gene_dictionary2, string_annotations[['preferred_name', 'id']].drop_duplicates(), left_on = 'synonymes', right_on= 'preferred_name',  how='left')
    gene_dictionary2 = gene_dictionary2.dropna(subset=['id'])
    gene_dictionary2 = gene_dictionary2[['id', 'dictionary_id']]
    gene_dictionary2 = gene_dictionary2.drop_duplicates().reset_index(drop = True)


    for i, n in enumerate(gene_dictionary2['dictionary_id']):
        if gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]] != gene_dictionary['id'][gene_dictionary['dictionary_id'] == n][gene_dictionary.index[gene_dictionary['dictionary_id'] == n][0]]:
            gene_dictionary['id'][gene_dictionary['dictionary_id'] == n] = int(gene_dictionary2['id'][i])
            
            
    gene_dictionary = gene_dictionary.rename(columns={"id": "id_string"})
    
    gene_dictionary = gene_dictionary.drop('preferred_name', axis = 1)
        
    gene_dictionary = gene_dictionary.to_dict(orient = 'list')
    
  
    
    string_dict['metadata'] = string_annotations_dict
    
    return string_dict, gene_dictionary



#Data interaction functions


def jbio_GOPa_prepare(path_in_use):
    
    
    #gene dictionary
    with open(path_in_use + '/gene_dictionary_jbio_annotated.json', 'r') as json_file:
        gene_dictionary = (json.load(json_file))
        
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    #load kegg
    with open(path_in_use + '/kegg_jbio_dict.json', 'r') as json_file:
        kegg = (json.load(json_file))
        
    
    kegg = pd.DataFrame(kegg)
    
   
    
    gene_dictionary_kegg = gene_dictionary[gene_dictionary['id_kegg'] == gene_dictionary['id_kegg']]
    gene_dictionary_kegg = gene_dictionary_kegg[['gene_name', 'id_kegg']]
    gene_dictionary_kegg_1 = pd.merge(gene_dictionary_kegg, kegg[['3rd', 'id']].drop_duplicates(), left_on = 'id_kegg', right_on= 'id',  how='left')
    gene_dictionary_kegg_1 = gene_dictionary_kegg_1[['gene_name', '3rd']]
    gene_dictionary_kegg_1.columns =  ['gene_name', 'GOPa']

    kegg = gene_dictionary_kegg_1
    
    kegg['source'] = 'KEGG'

    
    del gene_dictionary_kegg_1, gene_dictionary_kegg
    
    
    #load reactome
    with open(path_in_use + '/reactome_jbio_dict.json', 'r') as json_file:
        reactome_jbio = (json.load(json_file))
        
    reactome = pd.DataFrame(reactome_jbio['metadata'])
    reactome = reactome.explode(['path_name'])
    reactome = reactome[['path_name', 'id']]

    gene_dictionary_reactome = gene_dictionary[gene_dictionary['id_reactome'] == gene_dictionary['id_reactome']]
    gene_dictionary_reactome = gene_dictionary_reactome[['gene_name', 'id_reactome']]
    gene_dictionary_reactome = pd.merge(gene_dictionary_reactome, reactome[['path_name', 'id']].drop_duplicates(), left_on = 'id_reactome', right_on= 'id',  how='left')
    gene_dictionary_reactome = gene_dictionary_reactome[['gene_name', 'path_name']]
    gene_dictionary_reactome.columns = ['gene_name', 'GOPa']
    
    
    reactome = gene_dictionary_reactome
    reactome['source'] = 'REACTOME'

    del gene_dictionary_reactome
    
    
    #load GO-term
    with open(path_in_use + '/goterm_jbio_dict.json', 'r') as json_file:
        go_term_jbio = (json.load(json_file))
        
    go = pd.DataFrame(go_term_jbio['metadata'])
    
    gene_dictionary_go = gene_dictionary[gene_dictionary['id_go'] == gene_dictionary['id_go']]
    gene_dictionary_go = gene_dictionary_go[['gene_name', 'id_go']]
    gene_dictionary_go = pd.merge(gene_dictionary_go, go[['GO_id', 'id']].drop_duplicates(), left_on = 'id_go', right_on= 'id',  how='left')
    gene_dictionary_go = gene_dictionary_go[['gene_name', 'GO_id']]
    
    go2 = pd.DataFrame(go_term_jbio['connections'])
    go2 = go2[go2['obsolete'] == False]
    
    go2 = go2[~go2['name'].isin(list(set(go2['name_space'])))]
    
    go2['name_space'] = [x.upper() for x in go2['name_space']]
    
    name_mapping = dict(zip(['BIOLOGICAL_PROCESS', 'CELLULAR_COMPONENT', 'MOLECULAR_FUNCTION'], ['BP : ','CC : ','MF : ']))
    
    
    go2['role_sc'] = go2['name_space'].map(name_mapping)

    
    prefixes = ['rRNA','mRNA','snoRNA','lncRNA','piRNA','tRNA','miRNA','snRNA','siRNA', 'cGMP', 'mTOR', 'cAMP' , 'vRNA', 'snRNP']
    go2['name'] = [x[0].upper() + x[1:] if not any(x[:4] in prefix for prefix in prefixes) else x for x in go2['name']]



    gene_dictionary_go['GOPa'] = gene_dictionary_go['GO_id'] 
    
    
    name_mapping = dict(zip(go2['GO_id'], go2['role_sc'] + go2['name']))
    gene_dictionary_go['GOPa'] = gene_dictionary_go['GOPa'].map(name_mapping)
    
    go = gene_dictionary_go[['gene_name', 'GOPa', 'GO_id']]
    go = go.rename(columns = {'GO_id' : 'relation_id'})
    go['source'] = 'GO-TERM'
    
    go = go.dropna()
    
    

    
    del go2, name_mapping, go_term_jbio
    
    
    #load diseases
    with open(path_in_use + '/disease_jbio_dict.json', 'r') as json_file:
        disease = (json.load(json_file))
        
    disease = pd.DataFrame(disease)
    disease = disease[['disease', 'id']]

    gene_dictionary_disease = gene_dictionary[gene_dictionary['id_diseases'] == gene_dictionary['id_diseases']]
    gene_dictionary_disease = gene_dictionary_disease[['gene_name', 'id_diseases']]
    gene_dictionary_disease = pd.merge(gene_dictionary_disease, disease[['disease', 'id']].drop_duplicates(), left_on = 'id_diseases', right_on= 'id',  how='left')
    gene_dictionary_disease = gene_dictionary_disease[['gene_name', 'disease']]
    gene_dictionary_disease.columns = ['gene_name', 'GOPa']
    
    disease = gene_dictionary_disease
    
    disease['GOPa'] = [x[0].upper() + x[1:] for x in disease['GOPa']]

    
    disease['source'] = 'DISEASES'
    
    del gene_dictionary_disease
    
    
    
    #load viral diseases
    with open(path_in_use + '/viral_jbio_dict.json', 'r') as json_file:
        viral_disease = (json.load(json_file))
        
    viral_disease = pd.DataFrame(viral_disease)
    viral_disease = viral_disease[['virus_disease', 'id']]

    gene_dictionary_disease = gene_dictionary[gene_dictionary['id_viral_diseases'] == gene_dictionary['id_viral_diseases']]
    gene_dictionary_disease = gene_dictionary_disease[['gene_name', 'id_viral_diseases']]
    gene_dictionary_disease = pd.merge(gene_dictionary_disease, viral_disease[['virus_disease', 'id']].drop_duplicates(), left_on = 'id_viral_diseases', right_on= 'id',  how='left')
    gene_dictionary_disease = gene_dictionary_disease[['gene_name', 'virus_disease']]
    gene_dictionary_disease.columns = ['gene_name', 'GOPa']
    
    viral_disease = gene_dictionary_disease
    
    viral_disease['source'] = 'VIRAL'
    
    del gene_dictionary_disease

    GOPa_dis = pd.concat([disease, viral_disease])
    GOPa_dis = GOPa_dis.sort_values(by =['source', 'GOPa'])
    
    jdci = pd.DataFrame({'names':list(set(GOPa_dis['GOPa'])), 'relation_id':range(len(list(set(GOPa_dis['GOPa']))))})
    
    jdci['relation_id'] = [str(x) for x in jdci['relation_id']]
    jdci['relation_id'] = 'DIS:' + jdci['relation_id']
    
    GOPa_dis = pd.merge(GOPa_dis, jdci[['names', 'relation_id']], left_on = 'GOPa', right_on= 'names',  how='left')
        
    GOPa_dis = GOPa_dis.drop('names', axis = 1)
    
    GOPa_path = pd.concat([kegg, reactome])
    GOPa_path = GOPa_path.sort_values(by =['source', 'GOPa'])
    
    
    jdci = pd.DataFrame({'names':list(set(GOPa_path['GOPa'])), 'relation_id':range(len(list(set(GOPa_path['GOPa']))))})
    
    jdci['relation_id'] = [str(x) for x in jdci['relation_id']]
    jdci['relation_id'] = 'PA:' + jdci['relation_id']
    
    GOPa_path = pd.merge(GOPa_path, jdci[['names', 'relation_id']], left_on = 'GOPa', right_on= 'names',  how='left')
        
    GOPa_path = GOPa_path.drop('names', axis = 1)
    
    GOPa = pd.concat([go, GOPa_path, GOPa_dis])
    
    GOPa = GOPa.drop_duplicates()
    
    GOPa = pd.merge(GOPa, gene_dictionary[['gene_name', 'dictionary_id']], on = 'gene_name', how = 'left')
    
    prefixes = ['rRNA','mRNA','snoRNA','lncRNA','piRNA','tRNA','miRNA','snRNA','siRNA', 'cGMP', 'mTOR', 'cAMP' , 'vRNA', 'snRNP']
    GOPa['GOPa'] = [x[0].upper() + x[1:] if not any(x[:4] in prefix for prefix in prefixes) else x for x in GOPa['GOPa']]



    GOPa = GOPa.to_dict(orient = 'list')
    
    
    return GOPa



def gene_interactome_prepare(path_in_use, string_qn = 0.1):
    
    #gene dictionary
    with open(path_in_use + '/gene_dictionary_jbio_annotated.json', 'r') as json_file:
        gene_dictionary = (json.load(json_file))

    #load STRING
    with open(path_in_use + '/string_jbio_dict.json', 'r') as json_file:
        string_dict = (json.load(json_file))

    
    gene_dictionary = pd.DataFrame(gene_dictionary)
    
    # go_connections = pd.DataFrame(go_term_jbio['connections'])
    
    string_meta = pd.DataFrame(string_dict['metadata'])
    string = pd.DataFrame(string_dict['ppi'])

    
    string_meta = pd.merge(string_meta, gene_dictionary, left_on = 'id', right_on = 'id_string', how = 'left')

    string = pd.merge(string, string_meta[['preferred_name', 'dictionary_id']], left_on = 'protein1', right_on = 'preferred_name', how = 'left')
    string = string.rename(columns={"dictionary_id": 'id_1'})
    string = string[string['id_1'] == string['id_1']]



    string = pd.merge(string, string_meta[['preferred_name', 'dictionary_id']], left_on = 'protein2', right_on = 'preferred_name', how = 'left')
    string = string.rename(columns={"dictionary_id": 'id_2'})
    string = string[string['id_2'] == string['id_2']]

    string = string[string['combined_score'] > np.percentile(string['combined_score'], string_qn)]
    
    string = string.drop(columns=['protein1','protein2', 'preferred_name_x', 'preferred_name_y', 'combined_score'])
    
    string['source'] = 'STRING'
    
    del string_dict, string_meta
            
    #load IntAct
    with open(path_in_use + '/intact_jbio_dict.json', 'r') as json_file:
        intact_dict = (json.load(json_file))

    intact_dict = pd.DataFrame(intact_dict)

    intact_dict = intact_dict[intact_dict['species_1'] == intact_dict['species_2']]
    gene_dictionary = gene_dictionary[gene_dictionary['id_IntAct'] == gene_dictionary['id_IntAct']]
    name_mapping = dict(zip(gene_dictionary['id_IntAct'], gene_dictionary['dictionary_id']))
    
    

    intact_dict = intact_dict[['id_1', 'id_2', 'source', 'species_1']]
    
    intact_dict['id_1'] = intact_dict['id_1'].map(name_mapping)
    intact_dict['id_2'] = intact_dict['id_2'].map(name_mapping)

    intact_dict = intact_dict[intact_dict['id_1'] == intact_dict['id_1']]
    intact_dict = intact_dict[intact_dict['id_2'] == intact_dict['id_2']]
    
    intact_dict = intact_dict.rename(columns = {'species_1':'species'})
    
    string['species'][string['species'] == 'mouse'] = 'Mus musculus'
    string['species'][string['species'] == 'human'] = 'Homo sapiens'

    
    interaction = pd.concat([intact_dict, string])
    
    interaction = interaction.to_dict(orient = 'list')
  
    return interaction




def GOPa_interactions_prepare(path_in_use):
    
    GOPa = jbio_GOPa_prepare(path_in_use)
    GOPa = pd.DataFrame(GOPa)
        
    
    #load GO-term
    with open(path_in_use + '/goterm_jbio_dict.json', 'r') as json_file:
        go_term_jbio = (json.load(json_file))
    #tissue cell / specificity
        go_connections = pd.DataFrame(go_term_jbio['connections'])
    
    
    #gene dictionary
    with open(path_in_use + '/gene_dictionary_jbio_annotated.json', 'r') as json_file:
        gene_dictionary = (json.load(json_file))
        
    gene_dictionary = pd.DataFrame(gene_dictionary)  
    
    go_connections = go_connections[['GO_id', 'name', 'name_space', 'definition',
           'alternative_id', 'obsolete', 'is_a_ids', 'part_of_ids',
           'has_part_ids', 'regulates_ids', 'negatively_regulates_ids',
           'positively_regulates_ids']]
    
    
    GOPa_path = GOPa[GOPa['source'].isin(['KEGG', 'REACTOME'])]
    
    met_go = pd.DataFrame(go_term_jbio['metadata'])[['GO_id', 'id']]
    met_go = pd.merge(met_go, gene_dictionary[['dictionary_id', 'id_go']], left_on = 'id', right_on = 'id_go', how = 'left')
    
    met_go = met_go.drop(['id_go', 'id'], axis = 1)
    met_go = met_go[met_go['dictionary_id'] == met_go['dictionary_id']]
    
    met_go = pd.merge(met_go, GOPa_path[['relation_id', 'dictionary_id']],  on = 'dictionary_id', how = 'left')
    
    met_go = met_go[met_go['relation_id'] == met_go['relation_id']]
    
    met_go = met_go.groupby('GO_id')[['relation_id']].agg(list).reset_index()
    
    go_connections = pd.merge(go_connections, met_go, on = 'GO_id', how = 'left')
    
    
    GOPa_dis = GOPa[GOPa['source'].isin(['DISEASES', 'VIRAL'])]
    
    met_go = pd.DataFrame(go_term_jbio['metadata'])[['GO_id', 'id']]
    met_go = pd.merge(met_go, gene_dictionary[['dictionary_id', 'id_go']], left_on = 'id', right_on = 'id_go', how = 'left')
    
    met_go = met_go.drop(['id_go', 'id'], axis = 1)
    met_go = met_go[met_go['dictionary_id'] == met_go['dictionary_id']]
    
    met_go = pd.merge(met_go, GOPa_dis[['relation_id', 'dictionary_id']],  on = 'dictionary_id', how = 'left')
    
    met_go = met_go[met_go['relation_id'] == met_go['relation_id']]
    
    met_go = met_go.groupby('GO_id')[['relation_id']].agg(list).reset_index()
    
    
    go_connections = pd.merge(go_connections, met_go, on = 'GO_id', how = 'left')
    
    go_connections = go_connections.rename(columns = {'relation_id_x':'path_ids', 'relation_id_y':'disease_ids'})
    
    go_connections['disease_ids'][go_connections['disease_ids'] != go_connections['disease_ids']] = None
    go_connections['path_ids'][go_connections['path_ids'] != go_connections['path_ids']] = None
    
    go_connections = go_connections.reset_index(drop = True)

    go_connections = go_connections.to_dict()

    return go_connections




def specificity_prepare(path_in_use):
    
    #gene dictionary
    with open(path_in_use + '/gene_dictionary_jbio_annotated.json', 'r') as json_file:
        gene_dictionary = (json.load(json_file))
        
    gene_dictionary = pd.DataFrame(gene_dictionary)  
    
    #load HPA
    with open(path_in_use + '/HPA_jbio_dict.json', 'r') as json_file:
        HPA_jbio = (json.load(json_file))
        
    HPA_jbio = pd.DataFrame(HPA_jbio)
    

    
    #cell specificity
        
    RNA_tissue = HPA_jbio[['Gene', 'RNA tissue specificity', 'RNA tissue distribution', 'RNA tissue specificity score', 'RNA tissue specific nTPM', 'id']]
    RNA_tissue = RNA_tissue.dropna()
    RNA_tissue.columns = ['gene_name', 'specificity', 'distribution', 'standarized_specificity_score', 'nTPM', 'id']
    nTPM = RNA_tissue['nTPM'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename('nTPM')
    RNA_tissue = RNA_tissue.drop('nTPM', axis=1).join(nTPM)
    RNA_tissue[['name', 'TPM']] = RNA_tissue['nTPM'].str.split(':', n=1, expand=True)
    RNA_tissue['name'] = RNA_tissue['name'].str.replace(r' \d+$', '', regex=True)
    
    RNA_tissue['TPM'] = [float(x) for x in RNA_tissue['TPM']]
    RNA_tissue['log_TPM'] = np.log(RNA_tissue['TPM']+1)
    
    RNA_tissue['standarized_specificity_score'] = [float(x) for x in RNA_tissue['standarized_specificity_score']]
    RNA_tissue['log_standarized_specificity_score'] = np.log(RNA_tissue['standarized_specificity_score']+1)
    
    

    
    RNA_single_cell = HPA_jbio[['Gene', 'RNA single cell type specificity', 'RNA single cell type distribution', 'RNA single cell type specificity score', 'RNA single cell type specific nTPM', 'id']]
    RNA_single_cell = RNA_single_cell.dropna()
    RNA_single_cell.columns = ['gene_name', 'specificity', 'distribution', 'standarized_specificity_score', 'nTPM', 'id']
    nTPM = RNA_single_cell['nTPM'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename('nTPM')
    RNA_single_cell = RNA_single_cell.drop('nTPM', axis=1).join(nTPM)
    RNA_single_cell[['name', 'TPM']] = RNA_single_cell['nTPM'].str.split(':', n=1, expand=True)
    RNA_single_cell['name'] = RNA_single_cell['name'].str.replace(r' \d+$', '', regex=True)
    
    
    RNA_single_cell['TPM'] = [float(x) for x in RNA_single_cell['TPM']]
    RNA_single_cell['log_TPM'] = np.log(RNA_single_cell['TPM']+1)
    
    RNA_single_cell['standarized_specificity_score'] = [float(x) for x in RNA_single_cell['standarized_specificity_score']]
    RNA_single_cell['log_standarized_specificity_score'] = np.log(RNA_single_cell['standarized_specificity_score']+1)
    
    
    
    
    RNA_cancer = HPA_jbio[['Gene', 'RNA cancer specificity', 'RNA cancer distribution', 'RNA cancer specificity score', 'RNA cancer specific FPKM', 'id']]
    RNA_cancer = RNA_cancer.dropna()
    RNA_cancer.columns = ['gene_name', 'specificity', 'distribution', 'standarized_specificity_score', 'nTPM', 'id']
    nTPM = RNA_cancer['nTPM'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename('nTPM')
    RNA_cancer = RNA_cancer.drop('nTPM', axis=1).join(nTPM)
    RNA_cancer[['name', 'TPM']] = RNA_cancer['nTPM'].str.split(':', n=1, expand=True)
    RNA_cancer['name'] = RNA_cancer['name'].str.replace(r' \d+$', '', regex=True)
    
    
    RNA_cancer['TPM'] = [float(x) for x in RNA_cancer['TPM']]
    RNA_cancer['log_TPM'] = np.log(RNA_cancer['TPM']+1)

    
    RNA_cancer['standarized_specificity_score'] = [float(x) for x in RNA_cancer['standarized_specificity_score']]
    RNA_cancer['log_standarized_specificity_score'] = np.log(RNA_cancer['standarized_specificity_score']+1)
    
    
    
    
    RNA_brain = HPA_jbio[['Gene', 'RNA brain regional specificity', 'RNA brain regional distribution', 'RNA brain regional specificity score', 'RNA brain regional specific nTPM', 'id']]
    RNA_brain = RNA_brain.dropna()
    RNA_brain.columns = ['gene_name', 'specificity', 'distribution', 'standarized_specificity_score', 'nTPM', 'id']
    nTPM = RNA_brain['nTPM'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename('nTPM')
    RNA_brain = RNA_brain.drop('nTPM', axis=1).join(nTPM)
    RNA_brain[['name', 'TPM']] = RNA_brain['nTPM'].str.split(':', n=1, expand=True)
    RNA_brain['name'] = RNA_brain['name'].str.replace(r' \d+$', '', regex=True)
    
    RNA_brain['TPM'] = [float(x) for x in RNA_brain['TPM']]
    RNA_brain['log_TPM'] = np.log(RNA_brain['TPM']+1)
    
    
    RNA_brain['standarized_specificity_score'] = [float(x) for x in RNA_brain['standarized_specificity_score']]
    RNA_brain['log_standarized_specificity_score'] = np.log(RNA_brain['standarized_specificity_score']+1)
    
    
    
    
    RNA_blood = HPA_jbio[['Gene', 'RNA blood cell specificity', 'RNA blood cell distribution', 'RNA blood cell specificity score', 'RNA blood cell specific nTPM', 'id']]
    RNA_blood = RNA_blood.dropna()
    RNA_blood.columns = ['gene_name', 'specificity', 'distribution', 'standarized_specificity_score', 'nTPM', 'id']
    nTPM = RNA_blood['nTPM'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename('nTPM')
    RNA_blood = RNA_blood.drop('nTPM', axis=1).join(nTPM)
    RNA_blood[['name', 'TPM']] = RNA_blood['nTPM'].str.split(':', n=1, expand=True)
    RNA_blood['name'] = RNA_blood['name'].str.replace(r' \d+$', '', regex=True)
    
    
    RNA_blood['TPM'] = [float(x) for x in RNA_blood['TPM']]
    RNA_blood['log_TPM'] = np.log(RNA_blood['TPM']+1)
    
    RNA_blood['standarized_specificity_score'] = [float(x) for x in RNA_blood['standarized_specificity_score']]
    RNA_blood['log_standarized_specificity_score'] = np.log(RNA_blood['standarized_specificity_score']+1)
    
    
    
    
    RNA_blood_lineage = HPA_jbio[['Gene', 'RNA blood lineage specificity', 'RNA blood lineage distribution', 'RNA blood lineage specificity score', 'RNA blood lineage specific nTPM', 'id']]
    RNA_blood_lineage = RNA_blood_lineage.dropna()
    RNA_blood_lineage.columns = ['gene_name', 'specificity', 'distribution', 'standarized_specificity_score', 'nTPM', 'id']
    nTPM = RNA_blood_lineage['nTPM'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename('nTPM')
    RNA_blood_lineage = RNA_blood_lineage.drop('nTPM', axis=1).join(nTPM)
    RNA_blood_lineage[['name', 'TPM']] = RNA_blood_lineage['nTPM'].str.split(':', n=1, expand=True)
    RNA_blood_lineage['name'] = RNA_blood_lineage['name'].str.replace(r' \d+$', '', regex=True)
    
    
    RNA_blood_lineage['TPM'] = [float(x) for x in RNA_blood_lineage['TPM']]
    RNA_blood_lineage['log_TPM'] = np.log(RNA_blood_lineage['TPM']+1)
    
    RNA_blood_lineage['standarized_specificity_score'] = [float(x) for x in RNA_blood_lineage['standarized_specificity_score']]
    RNA_blood_lineage['log_standarized_specificity_score'] = np.log(RNA_blood_lineage['standarized_specificity_score']+1)
    
    
    
    
    
    RNA_cell_line = HPA_jbio[['Gene', 'RNA cell line specificity', 'RNA cell line distribution', 'RNA cell line specificity score', 'RNA cell line specific nTPM', 'id']]
    RNA_cell_line = RNA_cell_line.dropna()
    RNA_cell_line.columns = ['gene_name', 'specificity', 'distribution', 'standarized_specificity_score', 'nTPM', 'id']
    nTPM = RNA_cell_line['nTPM'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename('nTPM')
    RNA_cell_line = RNA_cell_line.drop('nTPM', axis=1).join(nTPM)
    RNA_cell_line[['name', 'TPM']] = RNA_cell_line['nTPM'].str.split(':', n=1, expand=True)
    RNA_cell_line['name'] = RNA_cell_line['name'].str.replace(r' \d+$', '', regex=True)
    
    
    RNA_cell_line['TPM'] = [float(x) for x in RNA_cell_line['TPM']]
    RNA_cell_line['log_TPM'] = np.log(RNA_cell_line['TPM']+1)
    
    RNA_cell_line['standarized_specificity_score'] = [float(x) for x in RNA_cell_line['standarized_specificity_score']]
    RNA_cell_line['log_standarized_specificity_score'] = np.log(RNA_cell_line['standarized_specificity_score']+1)
    
    
    
    RNA_mouse_brain_region = HPA_jbio[['Gene', 'RNA mouse brain regional specificity', 'RNA mouse brain regional distribution','RNA mouse brain regional specificity score', 'RNA mouse brain regional specific nTPM', 'id']]
    RNA_mouse_brain_region = RNA_mouse_brain_region.dropna()
    RNA_mouse_brain_region.columns = ['gene_name', 'specificity', 'distribution', 'standarized_specificity_score', 'nTPM', 'id']
    nTPM = RNA_mouse_brain_region['nTPM'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename('nTPM')
    RNA_mouse_brain_region = RNA_mouse_brain_region.drop('nTPM', axis=1).join(nTPM)
    RNA_mouse_brain_region[['name', 'TPM']] = RNA_mouse_brain_region['nTPM'].str.split(':', n=1, expand=True)
    RNA_mouse_brain_region['name'] = RNA_mouse_brain_region['name'].str.replace(r' \d+$', '', regex=True)
    
    
    RNA_mouse_brain_region['TPM'] = [float(x) for x in RNA_mouse_brain_region['TPM']]
    RNA_mouse_brain_region['log_TPM'] = np.log(RNA_mouse_brain_region['TPM']+1)
    
    RNA_mouse_brain_region['standarized_specificity_score'] = [float(x) for x in RNA_mouse_brain_region['standarized_specificity_score']]
    RNA_mouse_brain_region['log_standarized_specificity_score'] = np.log(RNA_mouse_brain_region['standarized_specificity_score']+1)
    
    ###
    RNA_tissue['source'] = 'RNA_tissue'
    
    RNA_single_cell['source'] = 'RNA_single_cell'
    
    RNA_cancer['source'] = 'RNA_cancer'
    
    RNA_brain['source'] = 'RNA_brain'
    
    RNA_blood['source'] = 'RNA_blood'
    
    RNA_blood_lineage['source'] = 'RNA_blood_lineage'
    
    RNA_cell_line['source'] = 'RNA_cell_line'
    
    RNA_mouse_brain_region['source'] = 'RNA_mouse_brain_region'
    
    
    SEQ = pd.concat([RNA_tissue, RNA_single_cell, RNA_cancer, RNA_brain, RNA_blood, RNA_blood_lineage, RNA_cell_line, RNA_mouse_brain_region])
    
    
    SEQ = pd.merge(SEQ, gene_dictionary[['dictionary_id', 'id_HPA']], left_on = 'id', right_on = 'id_HPA', how = 'left')
    SEQ = SEQ.drop(['id_HPA', 'id', 'nTPM'], axis = 1)
    SEQ = SEQ.dropna()
    
    SEQ['name'] = [x[0].upper() + x[1:] for x in SEQ['name']]

    SEQ = SEQ.to_dict(orient = 'list')
    ###
    
    
    #cellular location
    
    subcellular_location = HPA_jbio[['Gene', 'Subcellular location', 'id']]
    subcellular_location = subcellular_location.dropna()
    subcellular_location.columns = ['gene_name', 'location', 'id']
    subcellular_location['primary_location'] = 'subcellular_location'
    
    
    
    secretome_location = HPA_jbio[['Gene', 'Secretome location', 'id']]
    secretome_location = secretome_location.dropna()
    secretome_location.columns = ['gene_name', 'location', 'id']
    secretome_location['primary_location'] = 'secretome_location'
    
    
    
    
    subcellular_main_location = HPA_jbio[['Gene', 'Subcellular main location', 'id']]
    subcellular_main_location = subcellular_main_location.dropna()
    subcellular_main_location.columns = ['gene_name', 'location', 'id']
    subcellular_main_location['primary_location'] = 'subcellular_location'
    
    
    
    
    subcellular_additional_location = HPA_jbio[['Gene', 'Subcellular additional location',  'id']]
    subcellular_additional_location = subcellular_additional_location.dropna()
    subcellular_additional_location.columns = ['gene_name', 'location', 'id']
    subcellular_additional_location['primary_location'] = 'subcellular_location'
    
    
    location = pd.concat([subcellular_location, secretome_location, subcellular_main_location, subcellular_additional_location])
    
    locs = location['location'].str.split(',', expand=True).stack().reset_index(level=1, drop=True).rename('location')
    location = location.drop('location', axis=1).join(locs)
    location['location'] = location['location'].str.replace(r'^\s+|\s+$', '', regex=True)
    location['location'] = [x[0].upper() + x[1:].lower() for x in location['location']]
    
    location = pd.merge(location, gene_dictionary[['dictionary_id', 'id_HPA']], left_on = 'id', right_on = 'id_HPA', how = 'left')
    location = location.drop(['id_HPA', 'id'], axis = 1)
    location = location.dropna()
    location = location.drop_duplicates()
    
    location = location.reset_index(drop = True)
    
    
    location = location.to_dict(orient = 'list')
    
    #blood markers
    
    
    blood_levels = HPA_jbio[['Gene', 'Blood concentration - Conc. blood IM [pg/L]', 'Blood concentration - Conc. blood MS [pg/L]',  'id']]
    blood_levels.columns = ['gene_name', 'blood_concentration_IM[pg/L]', 'blood_concentration_MS[pg/L]',  'id']

    blood_levels = pd.merge(blood_levels, gene_dictionary[['dictionary_id', 'id_HPA']], left_on = 'id', right_on = 'id_HPA', how = 'left')
    blood_levels = blood_levels.drop(['id_HPA', 'id'], axis = 1)
    blood_levels = blood_levels[blood_levels['dictionary_id'] == blood_levels['dictionary_id']]

    blood_levels = blood_levels.to_dict(orient = 'list')


   
    

    final_dict = {'SEQ':SEQ, 'location':location, 'blood_levels':blood_levels}
    
    return final_dict
 


def GOPa_metadata_prepare(path_in_use):
    
    print('\n')
    print('GOPa data preparing ...')
    
    #gene dictionary
    with open(path_in_use + '/gene_dictionary_jbio_annotated.json', 'r') as json_file:
        gene_dictionary = (json.load(json_file))

    print('\n')
    print('Data standarization ...')
    GOPa = jbio_GOPa_prepare(path_in_use)

    print('\n')
    print('Data interactions preparing ...')
    GOPa_interactions = GOPa_interactions_prepare(path_in_use)
    
    print('\n')
    print('Gene/protein interactions preparing ...')
    GOPa_gene_interaction =  gene_interactome_prepare(path_in_use)
    
    print('\n')
    print('Gene/protein specificity preparing ...')
    GOPa_specificity = specificity_prepare(path_in_use)
    

    GOPa_metadata = {'gene_dictionary':gene_dictionary, 'GOPa':GOPa, 'GOPa_interactions':GOPa_interactions, 'GOPa_gene_interaction':GOPa_gene_interaction, 'GOPa_specificity':GOPa_specificity}
    
    
    
    return GOPa_metadata





def update_to_data(path = _path_inside, path_in_use = _path_in_inside):
    
    print('\n')
    print('Data update starts...')
    
    if not os.path.exists(path_in_use):
        try:
            os.makedirs(path_in_use)
            print(f"Directory '{path}' created successfully.")
        except OSError as e:
            print(f"Error creating the directory: {e}")
    else:
        print(f"Directory '{path}' already exists.")
    
    
        
    
    #LOAD MAIN GENE DICTIONARY
    #gene dictionary
    with open(path + '/gene_dictionary_jbio.json', 'r') as json_file:
        gene_dictionary = (json.load(json_file))
        
    
    ##REACTOME LOAD AND ADD TO DICT
    #load reactome
    with open(path + '/reactome_jbio.json', 'r') as json_file:
        reactome_jbio = (json.load(json_file))   
        
    
    
    reactome_jbio, gene_dictionary = reactome_to_gene_dict(reactome_jbio, gene_dictionary)
    
    
    
    with open(path_in_use + '/reactome_jbio_dict.json', 'w') as json_file:
        json.dump(reactome_jbio, json_file)
        
    del reactome_jbio
    
    
    ##HPA LOAD AND ADD TO DICT
    
    #load HPA
    with open(path + '/HPA_jbio.json', 'r') as json_file:
        HPA_jbio = (json.load(json_file))
        
        
    #HPA to dict
    
    HPA_jbio, gene_dictionary = HPA_to_gene_dict(HPA_jbio, gene_dictionary)
                      
    
    with open(path_in_use + '/HPA_jbio_dict.json', 'w') as json_file:
        json.dump(HPA_jbio, json_file)
    
    del HPA_jbio
    
    
    ##DISEASES LOAD AND ADD TO DICT
    
    #load diseases
    with open(path + '/diseases_jbio.json', 'r') as json_file:
        disease_dict_jbio = (json.load(json_file))
        
        
    #DISEASES
    
    
    disease_dict_jbio, gene_dictionary = diseases_to_gene_dict(disease_dict_jbio, gene_dictionary)
                      
    
    with open(path_in_use + '/disease_jbio_dict.json', 'w') as json_file:
        json.dump(disease_dict_jbio, json_file)
    
    del disease_dict_jbio
    
    
    ##VIRAL-DISEASES LOAD AND ADD TO DICT
    #VIRAL-DISEASES
    
    #load viral diseases
    with open(path + '/viral_diseases_jbio.json', 'r') as json_file:
        viral_dict_jbio = (json.load(json_file))
    
    
    viral_dict_jbio, gene_dictionary = viral_diseases_to_gene_dict(viral_dict_jbio, gene_dictionary)
                      
    
    with open(path_in_use + '/viral_jbio_dict.json', 'w') as json_file:
        json.dump(viral_dict_jbio, json_file)
    
    del viral_dict_jbio
    
    
    ##KEGG LOAD AND ADD TO DICT
    
    #load kegg
    with open(path + '/kegg_jbio.json', 'r') as json_file:
        kegg_jbio = (json.load(json_file))
        
    
    
    kegg_jbio, gene_dictionary = kegg_to_gene_dict(kegg_jbio, gene_dictionary)
                      
    with open(path_in_use + '/kegg_jbio_dict.json', 'w') as json_file:
        json.dump(kegg_jbio, json_file)
    
    del kegg_jbio
    
    
    ##GO-TERM LOAD AND ADD TO DICT
    #load GO-term
    with open(path + '/goterm_jbio.json', 'r') as json_file:
        go_term_jbio = (json.load(json_file))
    
    
    go_term_jbio, gene_dictionary = go_to_gene_dict(go_term_jbio, gene_dictionary)
    
    with open(path_in_use + '/goterm_jbio_dict.json', 'w') as json_file:
        json.dump(go_term_jbio, json_file)
    
    del go_term_jbio
    
    
    ##STRING LOAD AND ADD TO DICT
    
    
    #load intact
    with open(path + '/IntAct_jbio.json', 'r') as json_file:
        IntAct_dict = (json.load(json_file))
        
    
    IntAct_dict = pd.DataFrame(IntAct_dict)
    
    
    IntAct_dict, gene_dictionary = intact_to_gene_dict(IntAct_dict, gene_dictionary)
    
    
    with open(path_in_use + '/intact_jbio_dict.json', 'w') as json_file:
        json.dump(IntAct_dict, json_file)
        
    del IntAct_dict
    
    
    #load string
    with open(path + '/string_jbio.json', 'r') as json_file:
        string_dict = (json.load(json_file))
        
    
    string_dict, gene_dictionary = string_to_gene_dict(string_dict, gene_dictionary)
    
    
    with open(path_in_use + '/string_jbio_dict.json', 'w') as json_file:
        json.dump(string_dict, json_file)
    
    with open(path_in_use + '/gene_dictionary_jbio_annotated.json', 'w') as json_file:
        json.dump(gene_dictionary, json_file)
    
    del gene_dictionary, string_dict
    
    
    print('Data interaction starts...')
    
    
    
    GOPa_metadata = GOPa_metadata_prepare(path_in_use)
       
    with open(path_in_use + '/GOPa_metadata_dict.json', 'w') as json_file:
        json.dump(GOPa_metadata, json_file)
        
    print('\n')
    print('Process has finished...')


#full update def

def update_from_sources(path = _path_inside, path_in_use = _path_in_inside, password = None):
    
    """
    This function checks all source databases and updates the GOP database without supervision from the library author's side.
   

    Returns:
       Updated GOPa base.
   """
    
    try:
        import time
        print('\n')
        print('!!!WARNING!!! You have used the update_from_sources() option, the data in the GEDSpy library will be overwritten. We cannot guarantee that the authors of individual databases have not made changes that were not foreseen in GEDSpy and may cause unforeseen changes. If you want to restore the previous version of the data, reinstall the library. Data in the library will be updated and checked by the author in subsequent versions of the library. However, if you want access to the latest data, you can use it.')
        time.sleep(20)  
    
        update_downloading(path, password = password)
    
        update_to_data(path, path_in_use)
    
        try:
            os.remove(path + '/goterm_jbio.json')
            os.remove(path + '/reactome_jbio.json')
            os.remove(path + '/kegg_jbio.json')
            os.remove(path + '/string_jbio.json')
            os.remove(path + '/HPA_jbio.json')
            os.remove(path + '/viral_diseases_jbio.json')
            os.remove(path + '/diseases_jbio.json')
            os.remove(path + '/IntAct_jbio.json')
            os.remove(path + '/gene_dictionary_jbio.json')
            print(f"The temporary file was removed successfully")
        except OSError as e:
            print(f"Error deleting the file: {e}")
            
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")
  



def get_latest_version(package_name):
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    data = response.json()
    return data["info"]["version"]


def get_installed_version(package_name):
    try:
        version = pkg_resources.get_distribution(package_name).version
        return version
    except pkg_resources.DistributionNotFound:
        return "Not installed"
        
    
def check_update_availability(force = False):
    
    """
    This function checks if the newest version of GOPa data is available for the GEDSpy library and updates it.
   
    Args:
       force (bool) - if True user force update of GOPa data independent of the GEDSpy version
       
    Returns:
       Updated by the author the newest version of GOPa base.
   """
    
    try:
        _libd = str(get_package_directory())
    
        if get_latest_version('GEDSpy') != get_installed_version('GEDSpy') and force == False:
            print('\n')
            print('GOPa data in current version of GEDSpy is up to data. If you want download the newest data from original sources you can use update_from_sources() function')    
        elif get_latest_version('GEDSpy') != get_installed_version('GEDSpy') or force == True:
            
            print('\n')
            if force == False:
                print('GOPa data or GEDSpy version is not up-to-date.')
            elif force == True:
                print('GOPa data update was forced by the user')
            print('Update has started...')
            urllib.request.urlretrieve('https://github.com/jkubis96/GEDSpy/raw/v.2.0.0/data.zip', _libd + '/data.zip')
            shutil.rmtree(_libd + '/data')
            os.makedirs(_libd + '/data', exist_ok=True)
            with zipfile.ZipFile(_libd + '/data.zip', 'r') as zipf:
                zipf.extractall(_libd + '/data'),
            os.makedirs(_libd + '/data/tmp', exist_ok=True)
            os.remove(_libd + '/data.zip')
            
            print('\n')
            print('Update completed, if you want to check if the data version has changed, use "check_last_update()"')
            print('In addition, we recommend upgrading the GEDSpy version via pip by typing pip install GEDSpy --upgrade.')
    except:
        print('\n')
        print("Something went wrong. Try again or use update_from_sources() function.")




# get database 


def get_REACTOME(path_in_use = _path_in_inside):
    
    """
    This function gets the REACTOME data including the id to connect with REF_GENE by id_reactome

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       data_frame: REACTOME data
    """
    
    try:
        with open(path_in_use + '/reactome_jbio_dict.json', 'r') as json_file:
            reactome_jbio = (json.load(json_file))   
    
        return reactome_jbio
    
    except:
        print("Something went wrong. Check the function input data and try again!")



def get_REF_GEN(path_in_use = _path_in_inside):
    
    """
    This function gets the REF_GEN which is the combination of Homo sapiens and Mus musculus genomes for scientific use.

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       dict: Combination of Homo sapiens and Mus musculus genomes
    """
    
    try:
        
        with open(path_in_use + '/gene_dictionary_jbio_annotated.json', 'r') as json_file:
            gene_dictionary = (json.load(json_file))
    
        return gene_dictionary
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



def get_REF_GEN_RNA_SEQ(path_in_use = _path_in_inside):
    
    """
    This function gets the tissue-specific RNA-SEQ data including:
        -human_tissue_expression_HPA
        -human_tissue_expression_RNA_total_tissue
        -human_tissue_expression_fetal_development_circular
        -human_tissue_expression_illumina_bodyMap2

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       dict: Tissue specific RNA-SEQ data
    """
    
    try:
        
        with open(path_in_use + '/human_tissue_expression_HPA.json', 'r') as json_file:
            human_tissue_expression_HPA = json.load(json_file)
                    
        
        with open(path_in_use + '/human_tissue_expression_RNA_total_tissue.json', 'r') as json_file:
            human_tissue_expression_RNA_total_tissue = json.load(json_file)
            
        
        
        with open(path_in_use + '/human_tissue_expression_fetal_development_circular.json', 'r') as json_file:
            human_tissue_expression_fetal_development_circular = json.load(json_file)
            
        
        
        with open(path_in_use + '/human_tissue_expression_illumina_bodyMap2.json', 'r') as json_file:
            human_tissue_expression_illumina_bodyMap2 = json.load(json_file)
            

        rna_seq_list = {'human_tissue_expression_HPA':human_tissue_expression_HPA, 
                        'human_tissue_expression_RNA_total_tissue':human_tissue_expression_RNA_total_tissue, 
                        'human_tissue_expression_fetal_development_circular':human_tissue_expression_fetal_development_circular, 
                        'human_tissue_expression_illumina_bodyMap2':human_tissue_expression_illumina_bodyMap2}
    
        return rna_seq_list
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")
        
        
        
        
def get_HPA(path_in_use = _path_in_inside):
    
    """
    This function gets the HPA (Human Protein Atlas) data including the id to connect with REF_GENE by id_HPA

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       dict: HPA data
    """
    
    try:
        
        with open(path_in_use + '/HPA_jbio_dict.json', 'r') as json_file:
            HPA_jbio = (json.load(json_file))
            
            
    
        return HPA_jbio
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def get_DISEASES(path_in_use = _path_in_inside):
    
    """
    This function gets the DISEASES data including the id to connect with REF_GENE by id_diseases

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       dict: DISEASES data
    """
    
    try:
        
        #load diseases
        with open(path_in_use + '/disease_jbio_dict.json', 'r') as json_file:
            disease_dict_jbio = (json.load(json_file))
            
    
        return disease_dict_jbio
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



def get_ViMIC(path_in_use = _path_in_inside):
    
    """
    This function gets the ViMIC data including the id to connect with REF_GENE by id_viral_diseases

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       dict: ViMIC data
    """
    
    try:
        
        #load viral diseases
        with open(path_in_use + '/viral_jbio_dict.json', 'r') as json_file:
            viral_dict_jbio = (json.load(json_file))
        
    
        return viral_dict_jbio
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



def get_KEGG(path_in_use = _path_in_inside):
    
    """
    This function gets the KEGG data including the id to connect with REF_GENE by id_kegg

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       dict: KEGG data
    """
    
    try:
        
        #load kegg
        with open(path_in_use + '/kegg_jbio_dict.json', 'r') as json_file:
            kegg_jbio = (json.load(json_file))
             
    
        return kegg_jbio
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def get_GO(path_in_use = _path_in_inside):
    
    """
    This function gets the GO-TERM data including the id to connect with REF_GENE by id_go

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       data_frame: GO-TERM data
    """
    
    try:
    
        with open(path_in_use + '/goterm_jbio_dict.json', 'r') as json_file:
            go_term_jbio = (json.load(json_file))
       
    
        return go_term_jbio
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



def get_IntAct(path_in_use = _path_in_inside):
    
    """
    This function gets the IntAct data including the id to connect with REF_GENE by id_IntAct

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       data_frame: IntAct data
    """
    
    try:
        with open(path_in_use + '/intact_jbio_dict.json', 'r') as json_file:
            IntAct_dict = (json.load(json_file))
            
    
        return IntAct_dict
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")


def get_STRING(path_in_use = _path_in_inside):
    
    """
    This function gets the STRING data including the id to connect with REF_GENE by id_string

    Args:
       path_in_use (str) - path to data
       
     
    Returns:
       data_frame: STRING data
    """
    
    try:
        with open(path_in_use + '/string_jbio_dict.json', 'r') as json_file:
            string_dict = (json.load(json_file))
            
            
        return string_dict
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")
        
        
        
        

#######################################ANALYSIS########################################

#Analysis fucntions



def load_GOPa_meta(path_in_use = _path_in_inside):
    
    print('\n')
    print('Metadata loading...')

    with open(path_in_use + '/GOPa_metadata_dict.json', 'r') as json_file:
        GOPa_metadata = (json.load(json_file))
        
    return GOPa_metadata
    
    


def search_genes(gene_list:list, GOPa_metadata, species=None):
    
    """
    This function checks if the all genes provided in the list are in the data.

    Args:
       gene_list (list)- list of genes eg. ['KIT', 'EDNRB', 'PAX3'] 
       GOPa_metadata (dict) - metadata from load_GOPa_meta function 
       species (str or None) - ['human' / 'mouse' / 'both' / None] 
       
       If choose 'human' or 'mouse' you will obtain information about this species' genes. 
       If choose 'both' you will obtain information for genes that are available mutually for both species. 
       If choose None you will obtain information for all genes available in the metadata.       

    Returns:
       dict: A dictionary of all information available in metadata for genes provide in 'gene_list:'
   """
   
    print('\n')
    print('Searching genes from list in the GEDSpy data...')

    
    try:
        
        gene_list = [re.sub('.chr.*','', x) for x in gene_list]
        
        GOPa_metadata2 = copy.deepcopy(GOPa_metadata)
        
        gene_list = [x.upper() for x in gene_list]
        
        gene_list = [re.sub('-', '_', x) for x in gene_list]
        
        gene_dictionary = pd.DataFrame(GOPa_metadata2['gene_dictionary'])
        
        
        if species == 'human':
            tf_h = ['Homo sapiens' in x for x in gene_dictionary['species']]
            gene_dictionary_q = gene_dictionary[tf_h].copy()
            gene_dictionary_q = gene_dictionary_q.reset_index(drop = True)
            
            gene_dictionary_q['gene_name'] = [re.sub('-', '_', x) for x in gene_dictionary_q['gene_name']]
            
            synonymes = []
            for x in (gene_dictionary_q['synonymes']):
                if x == x:
                    synonymes = synonymes + x
            
            
            synonymes = [y.upper() for y in synonymes]
            synonymes = [re.sub('-', '_', x) for x in synonymes]
            
            genes = [y.upper() for y in gene_dictionary_q['gene_name']]
    
            genes_list = [f for f in gene_list if f in genes]
            
            synonymes_list = [f for f in gene_list if f in synonymes]
    
            synonymes_list =  [f for f in gene_list if f not in genes_list]
            
            not_found = [y for y in gene_list if y not in synonymes + genes]
            
            genes_df = gene_dictionary_q[gene_dictionary_q['gene_name'].isin(np.array(genes_list))].copy()
                    
            for i in synonymes_list:
                for indx in gene_dictionary_q.index:
                    if gene_dictionary_q['synonymes'][indx] == gene_dictionary_q['synonymes'][indx] and i in [re.sub('-', '_', x) for x in gene_dictionary_q['synonymes'][indx]]:
                        genes_tmp = pd.DataFrame(gene_dictionary_q.loc[indx,:]).transpose().copy()
                        genes_df = pd.concat([genes_df, genes_tmp]) 
            
        elif species == 'mouse':
            tf_h = ['Mus musculus' in x for x in gene_dictionary['species']]
            gene_dictionary_q = gene_dictionary[tf_h].copy()
            gene_dictionary_q = gene_dictionary_q.reset_index(drop = True)
            
            
            gene_dictionary_q['gene_name'] = [re.sub('-', '_', x) for x in gene_dictionary_q['gene_name']]

            
            synonymes = []
            for x in (gene_dictionary_q['synonymes']):
                if x == x:
                    synonymes = synonymes + x
            
            synonymes = [y.upper() for y in synonymes]
            synonymes = [re.sub('-', '_', x) for x in synonymes]
            
            genes = [y.upper() for y in gene_dictionary_q['gene_name']]
    
            genes_list = [f for f in gene_list if f in genes]
            
            synonymes_list = [f for f in gene_list if f in synonymes]
    
            synonymes_list =  [f for f in gene_list if f not in genes_list]
            
            not_found = [y for y in gene_list if y not in synonymes + genes]
            
            genes_df = gene_dictionary_q[gene_dictionary_q['gene_name'].isin(np.array(genes_list))].copy()
                    
            for i in synonymes_list:
                for indx in gene_dictionary_q.index:
                    if gene_dictionary_q['synonymes'][indx] == gene_dictionary_q['synonymes'][indx] and i in [re.sub('-', '_', x) for x in gene_dictionary_q['synonymes'][indx]]:
                        genes_tmp = pd.DataFrame(gene_dictionary_q.loc[indx,:]).transpose().copy()
                        genes_df = pd.concat([genes_df, genes_tmp]) 
    
        
        elif species == 'both':
            tf_h = ['Homo sapiens' in x and 'Mus musculus' in x for x in gene_dictionary['species']]
            gene_dictionary_q = gene_dictionary[tf_h].copy()
            gene_dictionary_q = gene_dictionary_q.reset_index(drop = True)
            
            gene_dictionary_q['gene_name'] = [re.sub('-', '_', x) for x in gene_dictionary_q['gene_name']]

            
            synonymes = []
            for x in (gene_dictionary_q['synonymes']):
                if x == x:
                    synonymes = synonymes + x
            
            synonymes = [y.upper() for y in synonymes]
            synonymes = [re.sub('-', '_', x) for x in synonymes]
            
            genes = [y.upper() for y in gene_dictionary_q['gene_name']]
    
            genes_list = [f for f in gene_list if f in genes]
            
            synonymes_list = [f for f in gene_list if f in synonymes]
    
            synonymes_list =  [f for f in gene_list if f not in genes_list]
            
            not_found = [y for y in gene_list if y not in synonymes + genes]
            
            genes_df = gene_dictionary_q[gene_dictionary_q['gene_name'].isin(np.array(genes_list))].copy()
                    
            for i in synonymes_list:
                for indx in gene_dictionary_q.index:
                    if gene_dictionary_q['synonymes'][indx] == gene_dictionary_q['synonymes'][indx] and i in [re.sub('-', '_', x) for x in gene_dictionary_q['synonymes'][indx]]:
                        genes_tmp = pd.DataFrame(gene_dictionary_q.loc[indx,:]).transpose().copy()
                        genes_df = pd.concat([genes_df, genes_tmp]) 
                
                       
                        
                        
        else:
            tf_h = ['Homo sapiens' in x or 'Mus musculus' in x for x in gene_dictionary['species']]
            gene_dictionary_q = gene_dictionary[tf_h].copy()
            gene_dictionary_q = gene_dictionary_q.reset_index(drop = True)
            
            gene_dictionary_q['gene_name'] = [re.sub('-', '_', x) for x in gene_dictionary_q['gene_name']]

            
            synonymes = []
            for x in (gene_dictionary_q['synonymes']):
                if x == x:
                    synonymes = synonymes + x
            
            synonymes = [y.upper() for y in synonymes]
            synonymes = [re.sub('-', '_', x) for x in synonymes]
            
            genes = [y.upper() for y in gene_dictionary_q['gene_name']]
    
            genes_list = [f for f in gene_list if f in genes]
            
            synonymes_list = [f for f in gene_list if f in synonymes]
    
            synonymes_list =  [f for f in gene_list if f not in genes_list]
            
            not_found = [y for y in gene_list if y not in synonymes + genes]
            
            genes_df = gene_dictionary_q[gene_dictionary_q['gene_name'].isin(np.array(genes_list))].copy()
                    
            for i in synonymes_list:
                for indx in gene_dictionary_q.index:
                    if gene_dictionary_q['synonymes'][indx] == gene_dictionary_q['synonymes'][indx] and i in [re.sub('-', '_', x) for x in gene_dictionary_q['synonymes'][indx]]:
                        genes_tmp = pd.DataFrame(gene_dictionary_q.loc[indx,:]).transpose().copy()
                        genes_df = pd.concat([genes_df, genes_tmp]) 
    
                        
        not_found = list(set(not_found)) 
        
        # data selection
        
        
        
        GOPa_results = GOPa_metadata2
        
        GOPa_results['gene_dictionary'] = genes_df.to_dict(orient = 'list')
        
        GOPa = pd.DataFrame(GOPa_results['GOPa'])
        
        GOPa = GOPa[GOPa['dictionary_id'].isin(list(genes_df['dictionary_id']))]
        
        GOPa_results['GOPa'] = GOPa.to_dict(orient = 'list')
    
        #
        GOPa_interactions = pd.DataFrame(GOPa_results['GOPa_interactions'])
         
        GOPa_interactions = GOPa_interactions[GOPa_interactions['GO_id'].isin(list(GOPa['relation_id'][GOPa['source'] == 'GO-TERM']))]
         
        GOPa_results['GOPa_interactions'] = GOPa_interactions.to_dict(orient = 'list')
        
        del GOPa_interactions
    
        #
        
        GOPa_genes = pd.DataFrame(GOPa_results['GOPa_gene_interaction'])
        
        GOPa_genes = GOPa_genes[GOPa_genes['id_1'].isin(list(genes_df['dictionary_id']))]
        
        GOPa_genes = GOPa_genes[GOPa_genes['id_2'].isin(list(genes_df['dictionary_id']))]
    
        GOPa_results['GOPa_gene_interaction'] = GOPa_genes.to_dict(orient = 'list')
        
        del GOPa_genes
        
        
        #
        
        GOPa_specificity = GOPa_results['GOPa_specificity']
        
        SEQ = pd.DataFrame(GOPa_specificity['SEQ'])
        
        SEQ = SEQ[SEQ['dictionary_id'].isin(list(genes_df['dictionary_id']))]
        
        GOPa_specificity['SEQ'] = SEQ.to_dict(orient = 'list')
        
        del SEQ
        
        location = pd.DataFrame(GOPa_specificity['location'])
        
        location = location[location['dictionary_id'].isin(list(genes_df['dictionary_id']))]
        
        GOPa_specificity['location'] = location.to_dict(orient = 'list')
        
        del location
        
        
        blood_levels = pd.DataFrame(GOPa_specificity['blood_levels'])
        
        blood_levels = blood_levels[blood_levels['dictionary_id'].isin(list(genes_df['dictionary_id']))]
        
        GOPa_specificity['blood_levels'] = blood_levels.to_dict(orient = 'list')
        
        del blood_levels
        
        
        
        GOPa_results['GOPa_specificity'] = GOPa_specificity
        
        if len(not_found) > 0:
            print('\n')
            print(str(len(not_found)) + ' out of ' + str(len(gene_list)) + ' values were not found')
            
        return GOPa_results, not_found
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")





def gopa_analysis(GOPa_data, GOPa_metadata):
    
    """
    This function conducts statistical / overrepresentation analysis on raw GOPa_data.

    Args:
       GOPa_data (dict) - raw GOPa_data from search_genes function
       GOPa_metadata (dict) - metadata from load_GOPa_meta function
     

    Returns:
       dict: A GOPa_data results with appropriate statistics
   """
   
    print('\n')
    print('Overrepresentation analysis of terms in GOPa data...')
    
    try:
       
        GOPa_metadata2 = copy.deepcopy(GOPa_metadata)
        GOPa_res = pd.DataFrame(GOPa_data['GOPa'])
        
        
        input_genes = int(len(set(GOPa_res['gene_name'])))
    
        total_genes = int(len(set(GOPa_metadata2['GOPa']['gene_name'])))
        
        GOPa_metadata2 = pd.DataFrame(GOPa_metadata2['GOPa'])
        
        GOPa_ocr = GOPa_metadata2.groupby('GOPa').agg({'dictionary_id': list}).reset_index()
        GOPa_ocr['ocr_n'] = [int(len(x)) for x in GOPa_ocr['dictionary_id']]
        
        GOPa_res = GOPa_res.groupby('GOPa').agg({'relation_id': list, 'dictionary_id': list, 'gene_name': list, 'source':max}).reset_index()
        
        GOPa_res['n'] = [int(len(x)) for x in GOPa_res['gene_name']]
        
        GOPa_res = pd.merge(GOPa_res, GOPa_ocr[['GOPa', 'ocr_n']], on = 'GOPa', how = 'left')
    
        GOPa_res['pct'] = GOPa_res['n']/GOPa_res['ocr_n']
        
        
        GOPa_res['p-val[BIN]'] = float('nan')
        GOPa_res['p-val[FISH]'] = float('nan')
        
        GOPa_res = GOPa_res.reset_index(drop = True)
    
        
    
        for n, p in enumerate(tqdm(GOPa_res['GOPa'])):  
            GOPa_res['p-val[BIN]'][n] = stats.binomtest(int(GOPa_res['n'][n]), int(input_genes), float(GOPa_res['ocr_n'][n]/total_genes), alternative='greater').pvalue
            observed_genes = int(GOPa_res['n'][n])
            not_observed_genes = int(GOPa_res['ocr_n'][n]) - observed_genes
            ontingency_table = [[observed_genes, not_observed_genes], [input_genes*(int(GOPa_res['ocr_n'][n])/total_genes), total_genes - (input_genes*(int(GOPa_res['ocr_n'][n])/total_genes))]]
            odds_ratio, GOPa_res['p-val[FISH]'][n] = stats.fisher_exact(ontingency_table, alternative='greater')
    
        GOPa_res['p-adj[BIN-BF]'] = GOPa_res['p-val[BIN]'] * len(GOPa_res['p-val[BIN]'])
        GOPa_res['p-adj[BIN-BF]'][GOPa_res['p-adj[BIN-BF]'] >= 1] = 1
        GOPa_res['p-adj[FISH-BF]'] = GOPa_res['p-val[FISH]'] * len(GOPa_res['p-val[FISH]'])
        GOPa_res['p-adj[FISH-BF]'][GOPa_res['p-adj[FISH-BF]'] >= 1] = 1
        
        GOPa_res = GOPa_res.sort_values(by='p-val[BIN]',  ascending=True)
    
        n = len(GOPa_res['p-val[BIN]'])
    
        GOPa_res['p-adj[BIN-FDR]'] = (GOPa_res['p-val[BIN]'] * n) / np.arange(1, n+1)
        
        GOPa_res = GOPa_res.sort_values(by='p-val[FISH]',  ascending=True)
    
        GOPa_res['p-adj[FISH-FDR]'] = (GOPa_res['p-val[FISH]'] * n) / np.arange(1, n+1)
        
        GOPa_res['p-adj[FISH-FDR]'][GOPa_res['p-adj[FISH-FDR]'] >= 1] = 1
        GOPa_res['p-adj[BIN-FDR]'][GOPa_res['p-adj[BIN-FDR]'] >= 1] = 1
    
                
        GOPa_data['GOPa'] = GOPa_res.to_dict(orient = 'list')
     
        return GOPa_data
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")

  




def gopa_interaction_analysis(GOPa_data):
    
    """
    This function conducts interaction analysis on GOPa_data.

    Args:
       GOPa_data (dict) - GOPa_data from gopa_analysis function
      

    Returns:
       dict: A GOPa_data results with data interactions
   """
   
    print('\n')
    print('Analysis of interactions of GOPa data...')

   
    try:
    
        GOPa_res = pd.DataFrame(GOPa_data['GOPa_interactions'])
        GOPa_enr = pd.DataFrame(GOPa_data['GOPa'])['relation_id']
        
        GOPa_list = []
        for x in GOPa_enr:
            GOPa_list = GOPa_list + x
        
        del GOPa_enr
    
    
        #grouping variables
        
        GOPa_is_a_ids = GOPa_res[['GO_id','is_a_ids']].explode('is_a_ids')
        
        GOPa_is_a_ids = GOPa_is_a_ids[GOPa_is_a_ids['is_a_ids'].isin(GOPa_list)]
        
        GOPa_is_a_ids.columns = ['A', 'B']
        
        GOPa_is_a_ids['color'] = 'gray'
        
        
    
        GOPa_part_of_ids = GOPa_res[['GO_id','part_of_ids']].explode('part_of_ids')
        
        GOPa_part_of_ids = GOPa_part_of_ids[GOPa_part_of_ids['part_of_ids'].isin(GOPa_list)]
        
        GOPa_part_of_ids.columns = ['A', 'B']
        
        GOPa_part_of_ids['color'] = 'gray'
    
    
        
        GOPa_has_part_ids = GOPa_res[['GO_id','has_part_ids']].explode('has_part_ids')
        
        GOPa_has_part_ids = GOPa_has_part_ids[GOPa_has_part_ids['has_part_ids'].isin(GOPa_list)]
    
        GOPa_has_part_ids.columns = ['A', 'B']
        
        GOPa_has_part_ids['color'] = 'gray'
    
        
      
        #path and disease
        
        #
        
        GOPa_disease_ids = GOPa_res[['GO_id','disease_ids']].explode('disease_ids')
        
        GOPa_disease_ids = GOPa_disease_ids[GOPa_disease_ids['disease_ids'].isin(GOPa_list)]
        
        
        GOPa_disease_ids.columns = ['A', 'B']
        
        GOPa_disease_ids['color'] = 'gray'
    
        #
        
    
        GOPa_path_ids = GOPa_res[['GO_id','path_ids']].explode('path_ids')
        
        GOPa_path_ids = GOPa_path_ids[GOPa_path_ids['path_ids'].isin(GOPa_list)]
        
        
        GOPa_path_ids.columns = ['A', 'B']
        
        GOPa_path_ids['color'] = 'gray'
        
        
        # GOPa_network = pd.concat([GOPa_is_a_ids, GOPa_part_of_ids, GOPa_has_part_ids, GOPa_disease_ids, GOPa_path_ids])
        
        
        
        
        #color variables 
    
        GOPa_regulates_ids = GOPa_res[['GO_id','regulates_ids']].explode('regulates_ids')
        
        GOPa_regulates_ids = GOPa_regulates_ids[GOPa_regulates_ids['regulates_ids'].isin(GOPa_list)]
        
        GOPa_regulates_ids.columns = ['A', 'B']
        
        GOPa_regulates_ids['color'] = 'gold'
        
        
        GOPa_regulates_ids = GOPa_regulates_ids[~GOPa_regulates_ids['A'].isin([None])]
        GOPa_regulates_ids = GOPa_regulates_ids[~GOPa_regulates_ids['B'].isin([None])]
        
        
        GOPa_regulates_ids['regulation'] = GOPa_regulates_ids['A'] + GOPa_regulates_ids['B']
    
    
        #
        
        GOPa_negatively_regulates_ids = GOPa_res[['GO_id','negatively_regulates_ids']].explode('negatively_regulates_ids')
    
        GOPa_negatively_regulates_ids = GOPa_negatively_regulates_ids[GOPa_negatively_regulates_ids['negatively_regulates_ids'].isin(GOPa_list)]
    
          
        GOPa_negatively_regulates_ids.columns = ['A', 'B']
        
        GOPa_negatively_regulates_ids['color'] = 'red'

        
        GOPa_negatively_regulates_ids = GOPa_negatively_regulates_ids[~GOPa_negatively_regulates_ids['A'].isin([None])]
        GOPa_negatively_regulates_ids = GOPa_negatively_regulates_ids[~GOPa_negatively_regulates_ids['B'].isin([None])]
        
        GOPa_negatively_regulates_ids['regulation'] = GOPa_negatively_regulates_ids['A'] + GOPa_negatively_regulates_ids['B']
        
        #
    
        GOPa_positively_regulates_ids = GOPa_res[['GO_id','positively_regulates_ids']].explode('positively_regulates_ids')
    
        GOPa_positively_regulates_ids = GOPa_positively_regulates_ids[GOPa_positively_regulates_ids['positively_regulates_ids'].isin(GOPa_list)]
          
        GOPa_positively_regulates_ids.columns = ['A', 'B']
        
        GOPa_positively_regulates_ids['color'] = 'green'
        
        
        GOPa_positively_regulates_ids = GOPa_positively_regulates_ids[~GOPa_positively_regulates_ids['A'].isin([None])]
        GOPa_positively_regulates_ids = GOPa_positively_regulates_ids[~GOPa_positively_regulates_ids['B'].isin([None])]
        
        GOPa_positively_regulates_ids['regulation'] = GOPa_positively_regulates_ids['A'] + GOPa_positively_regulates_ids['B']
    
    
        GOPa_network = pd.concat([GOPa_is_a_ids, GOPa_part_of_ids, GOPa_has_part_ids, GOPa_disease_ids, GOPa_path_ids, GOPa_positively_regulates_ids, GOPa_negatively_regulates_ids, GOPa_regulates_ids])

        GOPa_network = GOPa_network[~GOPa_network['A'].isin([None])]
        GOPa_network = GOPa_network[~GOPa_network['B'].isin([None])]
        
        
        GOPa_network['regulation'] = GOPa_network['A'] + GOPa_network['B']

        
        GOPa_network['color'][GOPa_network['regulation'].isin(list(GOPa_regulates_ids['regulation']))] = 'gold'
        GOPa_network['color'][GOPa_network['regulation'].isin(list(GOPa_negatively_regulates_ids['regulation']))] = 'red'
        GOPa_network['color'][GOPa_network['regulation'].isin(list(GOPa_positively_regulates_ids['regulation']))] = 'green'
    
        GOPa_network = GOPa_network.drop('regulation', axis = 1)
        
        GOPa_network = GOPa_network.drop_duplicates()
        
        GOPa_network = GOPa_network.to_dict(orient = 'list')
    
        GOPa_data['GOPa_interactions'] = GOPa_network
        
        return GOPa_data
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def gopa_specificity_analysis(GOPa_data, GOPa_metadata):
    
    """
    This function conducts statistical / overrepresentation analysis for 
    potential blood markers, tissue / cell specificity and cellular localization of genes / protein.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       GOPa_metadata (dict) - metadata from load_GOPa_meta function
     

    Returns:
       dict: A GOPa_data results with appropriate statistics
   """
   
    print('\n')
    print('Overrepresentation analysis of tissue, cellular and location specificity data...')
    
    
    try:
        
        GOPa_metadata2 = copy.deepcopy(GOPa_metadata)
        GOPa_res = GOPa_data['GOPa_specificity']
        GOPa_metadata2 = GOPa_metadata2['GOPa_specificity']
    
        # SEQ
        SEQ = pd.DataFrame(GOPa_res['SEQ'])
        SEQ_meta = pd.DataFrame(GOPa_metadata2['SEQ'])
    
        SEQ = SEQ[SEQ['distribution'] != 'Detected in all']
        
        SEQ = SEQ.reset_index(drop = True)
        
        input_genes = int(len(set(SEQ['gene_name'])))
        
        total_genes = int(len(set(SEQ_meta['gene_name'])))
    
        SEQ_meta = SEQ_meta.groupby('name').agg({'dictionary_id': list}).reset_index()
        SEQ_meta['ocr_n'] = [int(len(x)) for x in SEQ_meta['dictionary_id']]
        
        SEQ = SEQ.groupby('name').agg({'gene_name': list, 'dictionary_id': list, 'distribution':list, 'standarized_specificity_score': list,  'TPM': list, 'log_standarized_specificity_score': list,  'log_TPM': list, 'source':list}).reset_index()
        
        SEQ['n'] = [int(len(x)) for x in SEQ['dictionary_id']]
        
        SEQ = pd.merge(SEQ, SEQ_meta[['name', 'ocr_n']], on = 'name', how = 'left')
    
        SEQ['pct'] = SEQ['n']/SEQ['ocr_n']
        
        
        SEQ['p-val[BIN]'] = float('nan')
        SEQ['p-val[FISH]'] = float('nan')
        
        SEQ = SEQ.reset_index(drop = True)
        
        for n, p in enumerate(tqdm(SEQ['name'])):  
            SEQ['p-val[BIN]'][n] = stats.binomtest(int(SEQ['n'][n]), int(input_genes), float(SEQ['ocr_n'][n]/total_genes), alternative='greater').pvalue
            observed_genes = int(SEQ['n'][n])
            not_observed_genes = int(SEQ['ocr_n'][n]) - observed_genes
            ontingency_table = [[observed_genes, not_observed_genes], [input_genes*(int(SEQ['ocr_n'][n])/total_genes), total_genes - (input_genes*(int(SEQ['ocr_n'][n])/total_genes))]]
            odds_ratio, SEQ['p-val[FISH]'][n] = stats.fisher_exact(ontingency_table, alternative='greater')
            
    
        SEQ['p-adj[BIN-BF]'] = SEQ['p-val[BIN]'] * len(SEQ['p-val[BIN]'])
        SEQ['p-adj[BIN-BF]'][SEQ['p-adj[BIN-BF]'] >= 1] = 1
        SEQ['p-adj[FISH-BF]'] = SEQ['p-val[FISH]'] * len(SEQ['p-val[FISH]'])
        SEQ['p-adj[FISH-BF]'][SEQ['p-adj[FISH-BF]'] >= 1] = 1
        
        SEQ = SEQ.sort_values(by='p-val[BIN]',  ascending=True)
    
        n = len(SEQ['p-val[BIN]'])
    
        SEQ['p-adj[BIN-FDR]'] = (SEQ['p-val[BIN]'] * n) / np.arange(1, n+1)
        
        SEQ = SEQ.sort_values(by='p-val[FISH]',  ascending=True)
    
        SEQ['p-adj[FISH-FDR]'] = (SEQ['p-val[FISH]'] * n) / np.arange(1, n+1)
        
        SEQ['p-adj[FISH-FDR]'][SEQ['p-adj[FISH-FDR]'] >= 1] = 1
        SEQ['p-adj[BIN-FDR]'][SEQ['p-adj[BIN-FDR]'] >= 1] = 1
                
        GOPa_res['SEQ'] = SEQ.to_dict(orient = 'list')
        
        #location
        location = pd.DataFrame(GOPa_res['location'])
        location_meta = pd.DataFrame(GOPa_metadata2['location'])
    
        input_genes = int(len(set(location['gene_name'])))
        
        total_genes = int(len(set(location_meta['gene_name'])))
    
        location_meta = location_meta.groupby('location').agg({'dictionary_id': list}).reset_index()
        location_meta['ocr_n'] = [int(len(x)) for x in location_meta['dictionary_id']]
        
        location = location.groupby('location').agg({'gene_name': list, 'dictionary_id': list, 'primary_location':list}).reset_index()
        
        location['n'] = [int(len(x)) for x in location['dictionary_id']]
        
        location = pd.merge(location, location_meta[['location', 'ocr_n']], on = 'location', how = 'left')
    
        location['pct'] = location['n']/location['ocr_n']
        
        
        location['p-val[BIN]'] = float('nan')
        location['p-val[FISH]'] = float('nan')
        
        location = location.reset_index(drop = True)
        
        for n, p in enumerate(tqdm(location['location'])):  
            location['p-val[BIN]'][n] = stats.binomtest(int(location['n'][n]), int(input_genes), float(location['ocr_n'][n]/total_genes), alternative='greater').pvalue
            observed_genes = int(location['n'][n])
            not_observed_genes = int(location['ocr_n'][n]) - observed_genes
            ontingency_table = [[observed_genes, not_observed_genes], [input_genes*(int(location['ocr_n'][n])/total_genes), total_genes - (input_genes*(int(location['ocr_n'][n])/total_genes))]]
            odds_ratio, location['p-val[FISH]'][n] = stats.fisher_exact(ontingency_table, alternative='greater')
            
    
        location['p-adj[BIN-BF]'] = location['p-val[BIN]'] * len(location['p-val[BIN]'])
        location['p-adj[BIN-BF]'][location['p-adj[BIN-BF]'] >= 1] = 1
        location['p-adj[FISH-BF]'] = location['p-val[FISH]'] * len(location['p-val[FISH]'])
        location['p-adj[FISH-BF]'][location['p-adj[FISH-BF]'] >= 1] = 1
        
        location = location.sort_values(by='p-val[BIN]',  ascending=True)
    
        n = len(location['p-val[BIN]'])
    
        location['p-adj[BIN-FDR]'] = (location['p-val[BIN]'] * n) / np.arange(1, n+1)
        
        location = location.sort_values(by='p-val[FISH]',  ascending=True)
    
        location['p-adj[FISH-FDR]'] = (location['p-val[FISH]'] * n) / np.arange(1, n+1)
        
        location['p-adj[FISH-FDR]'][location['p-adj[FISH-FDR]'] >= 1] = 1
        location['p-adj[BIN-FDR]'][location['p-adj[BIN-FDR]'] >= 1] = 1
                
        GOPa_res['location'] = location.to_dict(orient = 'list')
        
        
        GOPa_data['GOPa_specificity'] = GOPa_res
        
     
        return GOPa_data
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")

  



def select_test(test, adj):
    try:
        test_string = ''

        if adj != None and adj.upper() in ['BF','FDR']:
            test_string = test_string + 'p-adj['
        else:
            test_string = test_string + 'p-val['
        
        
        if test != None and test.upper() == 'BIN':
            test_string = test_string + 'BIN'
        elif test != None and test.upper() == 'FISH':
            test_string = test_string + 'FISH'
        else:
            test_string = test_string + 'BIN'
            
        
        if adj != None and adj.upper() == 'BF':
            test_string = test_string + '-BF]'
        elif adj != None and adj.upper() == 'FDR':
            test_string = test_string + '-FDR]'
        else:
            test_string = test_string + ']'
        
        return test_string
    except:
        print('\n')
        print('Provided wrong test input!')
        
    
           

    

def GOPa_bar_plot(GOPa_data, GOPa_metadata, p_val = 0.05, test = 'FISH', adj = 'FDR', n = 25, side = 'right', color = 'blue', width = 10, bar_width = 0.5, count_type = 'p_val', details = 0.75, omit = None):
    
    """
    This function creates a bar plot of statistical / overrepresentation analysis terms from GO-TERM, PATHWAYS, DISEASES, and VIRAL (diseases related to viral infection)

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       GOPa_metadata (dict) - metadata from load_GOPa_meta function
       p_val (float) - value of minimal p_val for statistical test
       test (str) - type of statistical test ['FISH' - Fisher's exact test / 'BIN' - Binomial test]
       adj (str) - type of p_value correction ['BF' - Bonferroni correction / 'FDR' - False Discovery Rate (BH procedure)]
       n (int) - maximal number of bars on the graph
       side (str) - orientation of bars ['left' / 'right']
       color (str)- color of the bars
       width (float) - width of the graph
       bar_width (float) - width of the bars
       count_type (str) - type of amount of term representation on bars ['perc' - percent representation / 'p_val' - -log(p-val) of selected statistic test / 'num' - number representation]
       details (float) - degree detail for display GO-TERM and PATHWAYS where 1 is the maximal value and 0.1 is minimal [0.1-1]
       omit (list) - type of terms to omit in the graph eg. ['GO-TERM', 'KEGG', 'REACTOME', 'DISEASES', 'VIRAL'] or None
     
    Returns:
       dict of graphs: Dictionary of bar plots of overrepresentation analysis for GO-TERMS, PATHWAYS, DISEASES, and VIRAL
    """
    
    try:
        
        test_string = select_test(test, adj)
        figure_dict = {}
        
        
        sets = {'GO-TERM':['GO-TERM'], 'PATHWAYS':['KEGG', 'REACTOME'], 'DISEASES':['DISEASES'], 'VIRAL-INFECTIONS':['VIRAL']}
        
        GOPa = pd.DataFrame(GOPa_data['GOPa'])
        
        if omit != None:
            try:
                GOPa = GOPa[~GOPa['source'].isin(omit)]
            except:
                GOPa = GOPa[GOPa['source'] != omit]
        
        genes_number = int(len(set(GOPa.explode('gene_name')['gene_name'])))
        
        k_set = []
        for nk, k in enumerate(sets.keys()):
            if len(GOPa[GOPa['source'].isin(sets[k])].copy()) > 0:
                k_set.append(k)
                
        sets = {key: sets[key] for key in k_set}
            
        
        GOPa = GOPa[GOPa[str(test_string)] <= p_val]
        
        
        # Create subplots in a single row
        
        for nk, k in enumerate(sets.keys()):
            
                
                tmp = GOPa[GOPa['source'].isin(sets[k])].copy()
                tmp[test_string] = tmp[test_string] + np.min(tmp[test_string][tmp[test_string] != 0])/2
                tmp['-log(p-val)'] = -np.log(tmp[test_string])
                tmp['%'] = tmp['n'] / genes_number * 100
                
                
                detailed_tmp = pd.DataFrame(GOPa_metadata['GOPa'])
                detailed_tmp = detailed_tmp[detailed_tmp['source'].isin(sets[k])].copy().drop_duplicates()
                detailed_tmp = detailed_tmp.drop_duplicates()
                
                if k in ['PATHWAYS', 'GO-TERM'] and details != None:
                    detailed_tmp = Counter(list(detailed_tmp['GOPa']))
                    
                    detailed_tmp = pd.DataFrame(detailed_tmp.items(), columns=['GOPa', 'n'])
                                        
                    detailed_tmp = detailed_tmp.reset_index(drop = True)
                    detailed_tmp = list(detailed_tmp['GOPa'][detailed_tmp['n'] < np.quantile(detailed_tmp['n'][detailed_tmp['n'] > 100], details)])
                    
                    tmp = tmp[tmp['GOPa'].isin(detailed_tmp)]

                
            
                # Create a horizontal bar plot
                if count_type.upper() == 'perc'.upper():
                    tmp = tmp.sort_values(by='n', ascending=False)
                    tmp = tmp.reset_index(drop=True)
                    tmp = tmp.iloc[0:n,:]
                    
                    height = float(len(tmp['GOPa'])/2.5)
                    
                    fig, ax = plt.subplots(figsize=(width, height))
                    
                    ax.barh(tmp['GOPa'], tmp['%'], color=color, height = bar_width)
                    ax.set_xlabel('Percentr of genes [%]')
                    
                elif count_type.upper() == 'p_val'.upper():
                    tmp = tmp.sort_values(by='-log(p-val)', ascending=False)
                    tmp = tmp.reset_index(drop=True)
                    tmp = tmp.iloc[0:n,:]
                    
                    height = float(len(tmp['GOPa'])/2.5)
                    
                    fig, ax = plt.subplots(figsize=(width, height))
                    
                    ax.barh(tmp['GOPa'], tmp['-log(p-val)'], color=color, height = bar_width)
                    ax.set_xlabel('-log(p-val)')
                    
                else:
                    tmp = tmp.sort_values(by='n', ascending=False)
                    tmp = tmp.reset_index(drop=True)
                    tmp = tmp.iloc[0:n,:]
                    
                    height = float(len(tmp['GOPa'])/2.5)
                    
                    fig, ax = plt.subplots(figsize=(width, height))
                    
                    ax.barh(tmp['GOPa'], tmp['n'], color=color, height = bar_width)
                    ax.set_xlabel('Number of genes')
                    
            
                # Set labels and title
                
                ax.set_ylabel('')
                ax.set_title(k)
            
                # Invert y-axis to have names on the right
                ax.invert_yaxis()
         
            
                if side == 'right':
                    ax.yaxis.tick_right()
                    ax.set_yticks(range(len(tmp)))
                elif side == 'left':
                    ax.invert_xaxis()
                
                 
                
                figure_dict[k] = fig
                
        return figure_dict
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")
    
    


def save_plots(images:dict, path = '', prefix = '', img_format = 'svg'):
    """
    This function saves the plots which are included in the dictionary.
    
    
    Args:
       images (dict) - dictionary of graphs where dictionary.keys() will part of saved graph name
       path (str) - path to save the graphs
       prefix (str) - prefix for the saved graph names
       img_format (str) - format of saved graphs ['svg' / 'png' / 'jpg']
      
      
    Returns:
       file: Saved graphs in the indicated directory
    """
    
    try:
        
        for i in images.keys():
            images[i].savefig(path + prefix + '_' + str(i) + '.' + img_format,  format = img_format, bbox_inches = 'tight')
            
            
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def GOPa_network_vis(GOPa_data, GOPa_metadata, p_val = 0.05, test = 'FISH', adj = 'FDR', n_max = 10, list_of_terms = None, omit = None, details = 0.75, path = _path_tmp):
    
    """
    This function creates a visualization of the GOPa terms connections in the network format.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       GOPa_metadata (dict) - metadata from load_GOPa_meta function
       p_val (float) - value of minimal p_val for statistical test
       test (str) - type of statistical test ['FISH' - Fisher's exact test / 'BIN' - Binomial test]
       adj (str) - type of p_value correction ['BF' - Bonferroni correction / 'FDR' - False Discovery Rate (BH procedure)]
       n_max (int) - maximum number of interactions for each term
       list_of_terms (list) - list of terms to visualization their interactions ['term1', 'term2'] or None for highly occurrence interactions in GOPa_data
       omit (list) - type of terms to omit in the graph eg. ['KEGG', 'REACTOME', 'DISEASES', 'VIRAL'] or None
       details (float) - degree detail for display GO-TERM and PATHWAYS where 1 is the maximal value and 0.1 is minimal [0.1-1]. Work only if list_of_terms = None
       path (str) - path to temporarily save the visualization
       
       
    Returns:
       graph: Network graph for GO-TERMS, PATHWAYS, DISEASES, and VIRAL interactions
    """
    
    try:
        
        #screen parameter 
        
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        # Calculate desired height and width based on screen size
        desired_height = int(screen_height * 0.85)  
        desired_width = int(screen_width * 0.7)  
        
        
        #data network prepare
    
    
        test_string = select_test(test, adj)
        
        
        GOPa_interactions = pd.DataFrame(GOPa_data['GOPa_interactions'])
        
        GOPa = pd.DataFrame(GOPa_data['GOPa'])
        GOPa = GOPa[GOPa[str(test_string)] <= p_val]
        
        if omit != None:
            try:
                GOPa = GOPa[~GOPa['source'].isin(omit)]
            except:
                GOPa = GOPa[GOPa['source'] != omit]
        
        
        
        GOPa = GOPa[['GOPa','relation_id', 'source', 'ocr_n']].explode('relation_id')
        GOPa = GOPa.drop_duplicates()
        
        GOPa['color'] = float('nan')
        GOPa['color'][GOPa['source'] == 'GO-TERM'] = 'lightblue'
        GOPa['color'][GOPa['source'].isin(['REACTOME', 'KEGG'])] = 'orange'
        GOPa['color'][GOPa['source'] == 'DISEASES'] = 'purple'
        GOPa['color'][GOPa['source'] == 'VIRAL'] = 'gray'
        
        if list_of_terms != None:
            GOPa['color'][GOPa['GOPa'].isin(list_of_terms)] = 'aqua'
    
    
        
        
        GOPa_interactions = GOPa_interactions[GOPa_interactions['A'].isin(list(GOPa['relation_id']))]
        GOPa_interactions = GOPa_interactions[GOPa_interactions['B'].isin(list(GOPa['relation_id']))]
        
          
        name_mapping = dict(zip(GOPa['relation_id'], GOPa['source']))
        GOPa_interactions['source'] = GOPa_interactions['B'].map(name_mapping)
            
        GOPa_interactions['source'][GOPa_interactions['source'].isin(['KEGG','REACTOME'])] = 'PATHWAYS'
        GOPa['source'][GOPa['source'].isin(['KEGG','REACTOME'])] = 'PATHWAYS'


 
        name_mapping = dict(zip(GOPa['relation_id'], GOPa['GOPa']))
        GOPa_interactions['A'] = GOPa_interactions['A'].map(name_mapping)
        GOPa_interactions['B'] = GOPa_interactions['B'].map(name_mapping)
        
        

        
        interactions_df = pd.DataFrame()
        if list_of_terms != None:
            
            for tr in list_of_terms:
                if True in list(GOPa_interactions['A'].isin([tr])):
                    
                    tmp = GOPa_interactions[GOPa_interactions['A'].isin([tr])]
                    
                    
                    B = Counter(list(tmp['B']))
                    
                    B = pd.DataFrame(B.items(), columns=['GOPa', 'n'])
                    
                    B = B.sort_values(by = 'n', ascending = False)
                    
                    B = B.reset_index(drop = True)

                    if len(B['n']) > n_max:
                        tmp = tmp[tmp['B'].isin(B['GOPa'][B['n'] >= int(B['n'][math.ceil(n_max/len(set(tmp['source'])))])])]
                    else:
                        tmp = tmp
                    

                    tmp2 = GOPa_interactions[GOPa_interactions['B'].isin(list(tmp['B']))]
                    tmp3 = GOPa_interactions[GOPa_interactions['A'].isin(list(tmp2['A']))]
                    
                    
                    B = Counter(list(tmp3['B']))
                    
                    B = pd.DataFrame(B.items(), columns=['GOPa', 'n'])
                    
                    B = B.sort_values(by = 'n', ascending = False)
                    
                    B = B.reset_index(drop = True)
                    
                    
                    
                    if len(B['n']) > n_max:
                        tmp3 = tmp3[tmp3['B'].isin(list(B['GOPa'][B['n'] >= int(B['n'][math.ceil(n_max/len(set(tmp3['source'])))])]))]
                       
                    else:
                        tmp3 = tmp3
                        
                        
                    tmp = pd.concat([tmp, tmp3])

                    interactions_df = pd.concat([interactions_df, tmp])
                    

                elif True in list(GOPa_interactions['B'].isin([tr])):
                    
                    tmp = GOPa_interactions[GOPa_interactions['B'].isin([tr])]
                    
                     
                    A = Counter(list(tmp['A']))
                    
                    A = pd.DataFrame(A.items(), columns=['GOPa', 'n'])
                    
                    A = A.sort_values(by = 'n', ascending = False)
                    
                    A = A.reset_index(drop = True)
                    
                    
                    if len(A['n']) > n_max:
                        tmp = tmp[tmp['A'].isin(A['GOPa'][A['n'] >= int(A['n'][math.ceil(n_max/len(set(tmp['source'])))])])]
                    else:
                        tmp = tmp
                    

                    tmp2 = GOPa_interactions[GOPa_interactions['A'].isin(list(tmp['A']))]
                    
                    srcs = list(set(tmp2['source']))
                    list_of_B_term = []
                    
                    for s in srcs:
                        
                        gopa_list = Counter(list(tmp2['B'][tmp2['source'] == s]))
                        # Create a DataFrame from the Counter dictionary
                        gopa_list = pd.DataFrame(gopa_list.items(), columns=['GOPa', 'n'])
                        
                        gopa_list = gopa_list.sort_values(by = 'n', ascending = False)
                        
                        gopa_list = gopa_list.reset_index(drop = True)
                               
                        if int(n_max) > len(gopa_list['n']):
                            n_t = len(gopa_list['n']) - 1
                        else:
                            n_t = math.ceil(len(set(tmp2['source'])))
                        
                        
                        list_of_B_term = list_of_B_term + list(tmp2['B'][tmp2['B'].isin(list(gopa_list['GOPa'][gopa_list['n'] >= math.ceil(gopa_list['n'][n_t])]))])
                        
                    
                    tmp2 = tmp2[(tmp2['A'].isin(list(tmp['A']))) & (tmp2['B'].isin(list(list_of_B_term)))]

                    tmp = pd.concat([tmp,tmp2]) 
                    
                   
                    interactions_df = pd.concat([interactions_df,tmp])
            
            
            
            
                
            A = Counter(list(interactions_df['A']))
            
            A = pd.DataFrame(A.items(), columns=['GOPa', 'n'])
            
            A = A.sort_values(by = 'n', ascending = False)
            
            A = A.reset_index(drop = True)
            
            srcs = list(set(tmp2['source']))
            list_of_B_term = []
            
            for s in srcs:
                
                B = Counter(list(interactions_df['B'][interactions_df['source'] == s]))                
                B = pd.DataFrame(B.items(), columns=['GOPa', 'n'])
                
                B = B.sort_values(by = 'n', ascending = False)
                
                B = B.reset_index(drop = True)
                
                if len(B['n']) > n_max:
                    list_of_B_term = list_of_B_term + list(B['GOPa'][B['n'] >= int(B['n'][math.ceil(n_max/len(set(interactions_df['source'])))])]) 

                else:
                    list_of_B_term = list_of_B_term + list(B['GOPa']) 

                
            
            
            interactions_df = interactions_df[(interactions_df['A'].isin(list(A['GOPa'][A['n'] >= int(A['n'][math.ceil(n_max/len(set(interactions_df['source'])))])]) + list_of_terms)) & (interactions_df['B'].isin(list_of_B_term+ list_of_terms))]
              
                

            
        else:
            
            GOPa = GOPa[GOPa['GOPa'].isin(list(GOPa_interactions['A']) + list(GOPa_interactions['B']))]
            for nk, k in enumerate(set(GOPa['source'])):
                tmp = GOPa[GOPa['source'].isin([k])]
                      
                detailed_tmp = pd.DataFrame(GOPa_metadata['GOPa'])
                detailed_tmp['source'][detailed_tmp['source'].isin(['KEGG','REACTOME'])] = 'PATHWAYS'
                detailed_tmp = detailed_tmp[detailed_tmp['source'].isin([k])].copy().drop_duplicates()
                detailed_tmp = detailed_tmp.drop_duplicates()
                
                if k in ['PATHWAYS', 'GO-TERM'] and details != None:
                    detailed_tmp = Counter(list(detailed_tmp['GOPa']))
                    
                    detailed_tmp = pd.DataFrame(detailed_tmp.items(), columns=['GOPa', 'n'])
                                        
                    detailed_tmp = detailed_tmp.reset_index(drop = True)
                    detailed_tmp = list(detailed_tmp['GOPa'][detailed_tmp['n'] < np.quantile(detailed_tmp['n'][detailed_tmp['n'] > 100], details)])
                    
                    tmp = tmp[tmp['GOPa'].isin(detailed_tmp)]


            list_a = []
            list_b = []
            for src in list(set(GOPa_interactions['source'])):
                
                A = Counter(list(GOPa_interactions['A'][GOPa_interactions['source'] == src]))
                
                # Create a DataFrame from the Counter dictionary
                A = pd.DataFrame(A.items(), columns=['GOPa', 'n'])
                
                A = A.sort_values(by = 'n', ascending = False)
                
                A = A.reset_index(drop = True)
                
                if len(A['n']) > n_max:
                   list_a = list_a + list(GOPa_interactions['A'][GOPa_interactions['A'].isin(A['GOPa'][A['n'] >= int(A['n'][math.ceil(n_max/len(set(GOPa_interactions['source'])))])])])
                else:
                    list_a = list_a + list(GOPa_interactions['A'][GOPa_interactions['source'] == src])
                    
                    

                B = Counter(list(GOPa_interactions['B'][GOPa_interactions['source'] == src]))
                
                # Create a DataFrame from the Counter dictionary
                B = pd.DataFrame(B.items(), columns=['GOPa', 'n'])
                
                B = B.sort_values(by = 'n', ascending = False)
                
                B = B.reset_index(drop = True)
                
                if len(B['n']) > n_max:
                   list_b = list_b + list(GOPa_interactions['B'][GOPa_interactions['B'].isin(B['GOPa'][B['n'] >= int(B['n'][math.ceil(n_max/len(set(GOPa_interactions['source'])))])])])
                else:
                    list_b =  list_b + list(GOPa_interactions['B'][GOPa_interactions['source'] == src])

            
            interactions_df = GOPa_interactions[(GOPa_interactions['A'].isin(list_a)) & (GOPa_interactions['B'].isin(list_b))]
            
            
            A = Counter(list(interactions_df['A']))
            
            # Create a DataFrame from the Counter dictionary
            A = pd.DataFrame(A.items(), columns=['GOPa', 'n'])
            
            A = A.sort_values(by = 'n', ascending = False)
            
            A = A.reset_index(drop = True)
            
            interactions_df = interactions_df[interactions_df['A'].isin(A['GOPa'][A['n'] >= int(A['n'][math.ceil(n_max/len(set(interactions_df['source'])))])])]
            
            
        if len(interactions_df) > 0:
            
            

            GOPa_interactions = interactions_df
            GOPa_interactions = GOPa_interactions.reset_index(drop = True)
            
            gopa_list = list(GOPa_interactions['B']) + list(GOPa_interactions['A'])
            
            GOPa = GOPa[['GOPa', 'color']].drop_duplicates()
            
            GOPa = GOPa[GOPa['GOPa'].isin(gopa_list)]
            
            # Count the occurrences of each element in the list
            gopa_list = Counter(gopa_list)
            
            # Create a DataFrame from the Counter dictionary
            gopa_list = pd.DataFrame(gopa_list.items(), columns=['GOPa', 'weight'])
        
           
            GOPa = pd.merge(GOPa, gopa_list, on = 'GOPa', how = 'left')
        
        
                
            G = nx.Graph() 
        
         
            for _, row in GOPa.iterrows():
                node = row['GOPa']
                color = row['color']
                weight = np.log2(row['weight']*500)
                G.add_node(node, size = weight, color = color)
                
            for index, row in GOPa_interactions.iterrows():
                source = row['A']
                target = row['B']
                color = row['color']
                G.add_edge(source, target, color = color)
        
            
            
            # Create a pyvis Network instance
            net = Network(notebook=True, height=f"{desired_height}px", width=f"{desired_width}px")
            
            net.from_nx(G)
            
        
            net.repulsion(node_distance=150, spring_length=200)
            net.show_buttons(filter_=['nodes', 'physics'])
        
            
            net.show(os.path.join(path, 'tmp.html'))
            webbrowser.open(os.path.abspath(os.path.join(path, 'tmp.html')))
        
            
            return G
        
        else:
            print('\n \n')
    
            print('Lack of GO-TERM connections to all provided terms')
            
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")






def create_netowrk_GOPa_static(network, width = 16, height = 10, font_size = 10):
    
    """
    This function creates a network graph in static format.

    Args:
       network (network) - network from GOPa_network_vis or show_go_term functions
       width (float) - width of the graph
       height (float) - height of the graph
       font_size (float) - size of the fonts
      
     
    Returns:
       graph: Network in static format with the legend
    """
    
    
    try:
        # Layout
        pos = nx.spring_layout(network, seed = 123)  # You can choose a different layout algorithm
    
        # Drawing nodes and edges with attributes
        node_sizes = [data['size']*10 for node, data in network.nodes(data=True)]
        node_colors = [data['color'] for node, data in network.nodes(data=True)]
        edge_colors = [data['color'] for _, _, data in network.edges(data=True)]
    
        # Create the plot
        fig, ax = plt.subplots(figsize=(width, height))
        nx.draw_networkx_nodes(network, pos, node_size=node_sizes, node_color=node_colors)
        nx.draw_networkx_edges(network, pos, edge_color=edge_colors)
    
        node_labels = {node: node for node in network.nodes()}  
        node_labels = {node: node for node in network.nodes()}  
        labels = nx.draw_networkx_labels(network, pos, labels=node_labels, font_size=font_size, font_color="black", verticalalignment='center')
       
     
        texts = [labels[node] for node in labels]
        adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', alpha=.5))
        
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='TARGET-TERMS',
                   markerfacecolor='aqua', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='GO-TERM',
                   markerfacecolor='lightblue', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='PATHWAYS',
                   markerfacecolor='orange', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='DISEASES',
                   markerfacecolor='plum', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='VIRAL-DISEASES',
                   markerfacecolor='gray', markersize=10),
            Line2D([], [], linestyle='-', color='gold', label='regulate', linewidth=1),
            Line2D([], [], linestyle='-', color='red', label='negatively_regulates', linewidth=1),
            Line2D([], [], linestyle='-', color='green', label='positively_regulate', linewidth=1)
            ]
      
                  
                   
    
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.25, 1))
    
    
           
    
        plt.axis('off')  # Turn off axis
        plt.show()
        
        return fig
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")






def create_netowrk_gene_static(network, width = 12, height = 10, font_size = 10):
    
    """
    This function creates a network graph in static format.

    Args:
       network (network) - network from GOPa_network_vis or show_go_term functions
       width (float) - width of the graph
       height (float) - height of the graph
       font_size (float) - size of the fonts
      
     
    Returns:
       graph: Network in static format with the legend
    """
    
    
    try:
        # Layout
        pos = nx.spring_layout(network, seed = 123)  # You can choose a different layout algorithm
    
        # Drawing nodes and edges with attributes
        node_sizes = [data['size']*10 for node, data in network.nodes(data=True)]
        node_colors = [data['color'] for node, data in network.nodes(data=True)]
        edge_colors = [data['color'] for _, _, data in network.edges(data=True)]
    
        # Create the plot
        fig, ax = plt.subplots(figsize=(width, height))
        nx.draw_networkx_nodes(network, pos, node_size=node_sizes, node_color=node_colors)
        nx.draw_networkx_edges(network, pos, edge_color=edge_colors)
    
        node_labels = {node: node for node in network.nodes()}  
        node_labels = {node: node for node in network.nodes()}  
        labels = nx.draw_networkx_labels(network, pos, labels=node_labels, font_size=font_size, font_color="black", verticalalignment='center')
       
     
        texts = [labels[node] for node in labels]
        adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', alpha=.5))
    
           
    
        plt.axis('off')  # Turn off axis
        plt.show()
        
        return fig
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")






def create_netowrk_html(network, options = None):
    
    """
    This function creates a network graph in interactive HTML format with adjustment.

    Args:
       network (network) - network from GOPa_network_vis or show_go_term functions
       options (str) - string of options for interactive graph adjustment generated in GOPa_network_vis or show_go_term functions or None
      
     
    Returns:
       graph: Network in interactive HTML format
    """
    
    try:
        #screen parameter 
        
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        # Calculate desired height and width based on screen size
        desired_height = int(screen_height * 0.8)  
        desired_width = int(screen_width * 0.95)  
        
        #
        
        net = Network(notebook=True, height=f"{desired_height}px", width=f"{desired_width}px")
    
        net.from_nx(network)
        
        if options != None:
            net.set_options(options)
        
        return net
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")
        




def show_go_term(GOPa_metadata, GO_id = None, GO_name = None, n_max = 10, omit = None, path = _path_tmp):
    
    """
    This function creates a visualization of the GOPa terms connections in the network format.

    Args:
       GOPa_metadata (dict) - metadata from load_GOPa_meta function
       GO_id (str) - id of GO-TERM or None
       GO_name (str) - name of GO-TERM or None
       n_max (int) - maximum number of interactions for the term
       path (str) - path to temporarily save the visualization
       omit (list) - type of terms to omit in the graph eg. ['KEGG', 'REACTOME', 'DISEASES', 'VIRAL'] or None

      
     
    Returns:
       graph: Network for GO-TERM with its interactions
    """
    
    try:
    
        #screen parameter 
        
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        # Calculate desired height and width based on screen size
        desired_height = int(screen_height * 0.85)  
        desired_width = int(screen_width * 0.7)  
        
        
        #go-term network prepare
    
    
        
        GOPa_metadata2 = pd.DataFrame(copy.deepcopy(GOPa_metadata['GOPa_interactions']))
        
        GOPa_metadata2['name_space'] = [x.upper() for x in GOPa_metadata2['name_space']]
        
        name_mapping = dict(zip(['BIOLOGICAL_PROCESS', 'CELLULAR_COMPONENT', 'MOLECULAR_FUNCTION'], ['BP : ','CC : ','MF : ']))
        
        
        GOPa_metadata2['role_sc'] = GOPa_metadata2['name_space'].map(name_mapping)

        
        prefixes = ['rRNA','mRNA','snoRNA','lncRNA','piRNA','tRNA','miRNA','snRNA','siRNA', 'cGMP', 'mTOR', 'cAMP' , 'vRNA', 'snRNP']
        GOPa_metadata2['name'] = [x[0].upper() + x[1:] if not any(x[:4] in prefix for prefix in prefixes) else x for x in GOPa_metadata2['name']]
        GOPa_metadata2['name'] = GOPa_metadata2['role_sc'] + GOPa_metadata2['name']
        
        GOPa = pd.DataFrame(GOPa_metadata['GOPa'])
    
        
        if GO_id != None:
        
            GOPa_metadata2 = GOPa_metadata2[GOPa_metadata2['GO_id'] == GO_id]
        
        elif GO_name != None:
        
            GOPa_metadata2 = GOPa_metadata2[GOPa_metadata2['name'] == GO_name]
        else:
            GOPa_metadata2 = None
    
        try:
            #grouping variables
            
            GOPa_is_a_ids = GOPa_metadata2[['GO_id','is_a_ids']].explode('is_a_ids')
                
            GOPa_is_a_ids.columns = ['A', 'B']
                
            
        
            GOPa_part_of_ids = GOPa_metadata2[['GO_id','part_of_ids']].explode('part_of_ids')
            
            GOPa_part_of_ids.columns = ['A', 'B']
        
        
        
            
            GOPa_has_part_ids = GOPa_metadata2[['GO_id','has_part_ids']].explode('has_part_ids')
            
            GOPa_has_part_ids.columns = ['A', 'B']
        
            
        
            
            GOPa_regulates_ids = GOPa_metadata2[['GO_id','regulates_ids']].explode('regulates_ids')
                
            GOPa_regulates_ids.columns = ['A', 'B']
            
            
            
            GOPa_regulates_ids = GOPa_regulates_ids[~GOPa_regulates_ids['A'].isin([None])]
            GOPa_regulates_ids = GOPa_regulates_ids[~GOPa_regulates_ids['B'].isin([None])]
            
            
            GOPa_regulates_ids['regulation'] = GOPa_regulates_ids['A'] + GOPa_regulates_ids['B']
        
        
            #
            
            GOPa_negatively_regulates_ids = GOPa_metadata2[['GO_id','negatively_regulates_ids']].explode('negatively_regulates_ids')
        
            GOPa_negatively_regulates_ids.columns = ['A', 'B']
            
            
            GOPa_negatively_regulates_ids = GOPa_negatively_regulates_ids[~GOPa_negatively_regulates_ids['A'].isin([None])]
            GOPa_negatively_regulates_ids = GOPa_negatively_regulates_ids[~GOPa_negatively_regulates_ids['B'].isin([None])]
            
            
            GOPa_negatively_regulates_ids['regulation'] = GOPa_negatively_regulates_ids['A'] + GOPa_negatively_regulates_ids['B']
            
            #
        
            GOPa_positively_regulates_ids = GOPa_metadata2[['GO_id','positively_regulates_ids']].explode('positively_regulates_ids')
              
            GOPa_positively_regulates_ids.columns = ['A', 'B']
            
                        
            GOPa_positively_regulates_ids = GOPa_positively_regulates_ids[~GOPa_positively_regulates_ids['A'].isin([None])]
            GOPa_positively_regulates_ids = GOPa_positively_regulates_ids[~GOPa_positively_regulates_ids['B'].isin([None])]
            
            
            GOPa_positively_regulates_ids['regulation'] = GOPa_positively_regulates_ids['A'] + GOPa_positively_regulates_ids['B']
            
            
            GOPa_network = pd.concat([GOPa_is_a_ids, GOPa_part_of_ids, GOPa_has_part_ids, GOPa_positively_regulates_ids, GOPa_negatively_regulates_ids, GOPa_regulates_ids])
            
            GOPa_network = GOPa_network[~GOPa_network['A'].isin([None])]
            GOPa_network = GOPa_network[~GOPa_network['B'].isin([None])]
        
        
            
        
            det_list = set(list(list(GOPa_network['A']) + list(GOPa_network['B'])))
            
            GOPa_metadata2 = pd.DataFrame(copy.deepcopy(GOPa_metadata['GOPa_interactions']))
            
            GOPa = pd.DataFrame(GOPa_metadata['GOPa'])
        
        
            GOPa_metadata2 = GOPa_metadata2[GOPa_metadata2['GO_id'].isin(det_list)]
                
        
            #grouping variables
            
            GOPa_is_a_ids = GOPa_metadata2[['GO_id','is_a_ids']].explode('is_a_ids')
                
            GOPa_is_a_ids.columns = ['A', 'B']
            
            
            GOPa_is_a_ids['color'] = 'gray'
            
            
        
            GOPa_part_of_ids = GOPa_metadata2[['GO_id','part_of_ids']].explode('part_of_ids')
            
            GOPa_part_of_ids.columns = ['A', 'B']
        
            
            GOPa_part_of_ids['color'] = 'gray'
        
        
            
            GOPa_has_part_ids = GOPa_metadata2[['GO_id','has_part_ids']].explode('has_part_ids')
            
            GOPa_has_part_ids.columns = ['A', 'B']
        
            
            GOPa_has_part_ids['color'] = 'gray'
        
            
          
            #path and disease
            
            #
            
            GOPa_disease_ids = GOPa_metadata2[['GO_id','disease_ids']].explode('disease_ids')    
            
            GOPa_disease_ids.columns = ['A', 'B']
        
            
            GOPa_disease_ids['color'] = 'gray'
        
            #
            
        
            GOPa_path_ids = GOPa_metadata2[['GO_id','path_ids']].explode('path_ids')    
            
            GOPa_path_ids.columns = ['A', 'B']
        
            
            GOPa_path_ids['color'] = 'gray'
            
            
                
            #color variables 
        
            GOPa_regulates_ids = GOPa_metadata2[['GO_id','regulates_ids']].explode('regulates_ids')
                
            GOPa_regulates_ids.columns = ['A', 'B']
            
            GOPa_regulates_ids['color'] = 'gold'

            
            
            GOPa_regulates_ids = GOPa_regulates_ids[~GOPa_regulates_ids['A'].isin([None])]
            GOPa_regulates_ids = GOPa_regulates_ids[~GOPa_regulates_ids['B'].isin([None])]
            
            
            GOPa_regulates_ids['regulation'] = GOPa_regulates_ids['A'] + GOPa_regulates_ids['B']
        
        
            #
            
            GOPa_negatively_regulates_ids = GOPa_metadata2[['GO_id','negatively_regulates_ids']].explode('negatively_regulates_ids')
        
            GOPa_negatively_regulates_ids.columns = ['A', 'B']
            
            GOPa_negatively_regulates_ids['color'] = 'red'

            
            GOPa_negatively_regulates_ids = GOPa_negatively_regulates_ids[~GOPa_negatively_regulates_ids['A'].isin([None])]
            GOPa_negatively_regulates_ids = GOPa_negatively_regulates_ids[~GOPa_negatively_regulates_ids['B'].isin([None])]
            
            
            GOPa_negatively_regulates_ids['regulation'] = GOPa_negatively_regulates_ids['A'] + GOPa_negatively_regulates_ids['B']
            
            #
        
            GOPa_positively_regulates_ids = GOPa_metadata2[['GO_id','positively_regulates_ids']].explode('positively_regulates_ids')
              
            GOPa_positively_regulates_ids.columns = ['A', 'B']
            
            
            GOPa_positively_regulates_ids['color'] = 'green'
            
            GOPa_positively_regulates_ids = GOPa_positively_regulates_ids[~GOPa_positively_regulates_ids['A'].isin([None])]
            GOPa_positively_regulates_ids = GOPa_positively_regulates_ids[~GOPa_positively_regulates_ids['B'].isin([None])]
            
            
            GOPa_positively_regulates_ids['regulation'] = GOPa_positively_regulates_ids['A'] + GOPa_positively_regulates_ids['B']
        
        
            GOPa_network = pd.concat([GOPa_is_a_ids, GOPa_part_of_ids, GOPa_has_part_ids, GOPa_disease_ids, GOPa_path_ids, GOPa_positively_regulates_ids, GOPa_negatively_regulates_ids, GOPa_regulates_ids])

            GOPa_network = GOPa_network[~GOPa_network['A'].isin([None])]
            GOPa_network = GOPa_network[~GOPa_network['B'].isin([None])]
            
        
            GOPa_network['regulation'] = GOPa_network['A'] + GOPa_network['B']
            
            
            GOPa_network['color'][GOPa_network['regulation'].isin(list(GOPa_regulates_ids['regulation']))] = 'gold'
            GOPa_network['color'][GOPa_network['regulation'].isin(list(GOPa_negatively_regulates_ids['regulation']))] = 'red'
            GOPa_network['color'][GOPa_network['regulation'].isin(list(GOPa_positively_regulates_ids['regulation']))] = 'green'
        
            GOPa_network = GOPa_network.drop('regulation', axis = 1)
            
            GOPa_network = GOPa_network.drop_duplicates()
            

            gopa_list = list(set(list(GOPa_network['A']) + list(GOPa_network['B'])))
            
            GOPa = GOPa[GOPa['relation_id'].isin(gopa_list)]    
            GOPa = GOPa[['GOPa','relation_id', 'source']].explode('relation_id')
            GOPa = GOPa.drop_duplicates()
            
            GOPa['color'] = float('nan')
            GOPa['color'][GOPa['source'] == 'GO-TERM'] = 'lightblue'
            GOPa['color'][GOPa['source'].isin(['REACTOME', 'KEGG'])] = 'orange'
            GOPa['color'][GOPa['source'] == 'DISEASES'] = 'purple'
            GOPa['color'][GOPa['source'] == 'VIRAL'] = 'gray'
            
            if omit != None:
                try:
                    GOPa = GOPa[~GOPa['source'].isin(omit)]
                except:
                    GOPa = GOPa[GOPa['source'] != omit]
            
            go_without_gene = pd.DataFrame(get_GO()['connections'])
            go_without_gene = go_without_gene[go_without_gene['obsolete'] == False]
            
            name_mapping = dict(zip(list(GOPa['relation_id']) + list(go_without_gene['GO_id']), list(GOPa['source']) + list(['GO-TERM']*len(list(go_without_gene['GO_id'])))))
            GOPa_network['source'] = GOPa_network['B'].map(name_mapping)
            
            
            go_without_gene['name_space'] = [x.upper() for x in go_without_gene['name_space']]
            
            name_mapping = dict(zip(['BIOLOGICAL_PROCESS', 'CELLULAR_COMPONENT', 'MOLECULAR_FUNCTION'], ['BP : ','CC : ','MF : ']))
            
            
            go_without_gene['role_sc'] = go_without_gene['name_space'].map(name_mapping)

            
            prefixes = ['rRNA','mRNA','snoRNA','lncRNA','piRNA','tRNA','miRNA','snRNA','siRNA', 'cGMP', 'mTOR', 'cAMP' , 'vRNA', 'snRNP']
            go_without_gene['name'] = [x[0].upper() + x[1:] if not any(x[:4] in prefix for prefix in prefixes) else x for x in go_without_gene['name']]
            
            
            name_mapping = dict(zip(list(go_without_gene['GO_id']) + list(GOPa['relation_id']),   list(go_without_gene['role_sc'] + go_without_gene['name']) + list(GOPa['GOPa'])))
            
            GOPa_network['A'] = GOPa_network['A'].map(name_mapping)
            GOPa_network['B'] = GOPa_network['B'].map(name_mapping)
            
            del go_without_gene, GOPa_metadata2
            
            
            
            GOPa_network = GOPa_network.dropna()
            
            
            if omit != None:
                try:
                    GOPa_network = GOPa_network[~GOPa_network['source'].isin(omit)]
                except:
                    GOPa_network = GOPa_network[GOPa_network['source'] != omit]
                    
                    
            GOPa_network['source'][GOPa_network['source'].isin(['KEGG','REACTOME'])] = 'PATHWAYS'
            
            if len(GOPa_network) > 0:  
                
                
                srcs = list(set(GOPa_network['source']))
                list_of_B_term = []
                
                for s in srcs:
                    if s != 'GO-TERM':
                        for a_term in set(GOPa_network['A'][GOPa_network['source'].isin([s])]):
                           
                            gopa_list = Counter(list(GOPa_network['B'][GOPa_network['A'] == a_term]))
                            
                            # Create a DataFrame from the Counter dictionary
                            gopa_list = pd.DataFrame(gopa_list.items(), columns=['GOPa', 'n'])
                            
                            gopa_list = gopa_list.sort_values(by = 'n', ascending = False)
                            
                            gopa_list = gopa_list.reset_index(drop = True)
                                   
                            if int(n_max/len(set(GOPa_network['source']))) > len(gopa_list['n']):
                                n_t = len(gopa_list['n']) - 1
                            else:
                                n_t = math.ceil(n_max/len(set(GOPa_network['source'])))
                                
                                
                            list_of_B_term = list_of_B_term + list(gopa_list['GOPa'][gopa_list['n'] >= math.ceil(gopa_list['n'][n_t])])
                        
                
        
                GOPa_network = GOPa_network[GOPa_network['B'].isin(list_of_B_term)]
                
                GOPa_network1 = GOPa_network[GOPa_network['source'] == 'GO-TERM']
                GOPa_network2 = GOPa_network[GOPa_network['source'] != 'GO-TERM']
                
                
                srcs = list(set(GOPa_network2['source']))
                list_of_B_term = []
                
                for s in srcs:
                    
                    gopa_list = Counter(list(GOPa_network2['B'][GOPa_network2['source'] == s]))
                    # Create a DataFrame from the Counter dictionary
                    gopa_list = pd.DataFrame(gopa_list.items(), columns=['GOPa', 'n'])
                    
                    gopa_list = gopa_list.sort_values(by = 'n', ascending = False)
                    
                    gopa_list = gopa_list.reset_index(drop = True)
                           
                    if int(n_max) > len(gopa_list['n']):
                        n_t = len(gopa_list['n']) - 1
                    else:
                        n_t = math.ceil(len(set(GOPa_network2['source'])))
                    
                    
                    list_of_B_term = list_of_B_term + list(gopa_list['GOPa'][gopa_list['n'] >= math.ceil(gopa_list['n'][n_t])])
            
                GOPa_network2 = GOPa_network2[GOPa_network2['B'].isin(list_of_B_term)]
               
                GOPa_network = pd.concat([GOPa_network1, GOPa_network2])
                GOPa_network = GOPa_network.reset_index(drop = True)
                
                gopa_list = list(GOPa_network['B']) + list(GOPa_network['A'])
                
                GOPa = GOPa[['GOPa', 'color']].drop_duplicates()
                
                GOPa = GOPa[GOPa['GOPa'].isin(gopa_list)]
                
                # Count the occurrences of each element in the list
                gopa_list = Counter(gopa_list)
                
                # Create a DataFrame from the Counter dictionary
                gopa_list = pd.DataFrame(gopa_list.items(), columns=['GOPa', 'weight'])
            
                
                GOPa_network = GOPa_network.drop_duplicates()
        
                GOPa = pd.merge(GOPa, gopa_list, on = 'GOPa', how = 'right')
                GOPa['color'][GOPa['color'] != GOPa['color']] = 'lightblue'
            
                    
                G = nx.Graph() 
            
             
                for _, row in tqdm(GOPa.iterrows()):
                    node = row['GOPa']
                    color = row['color']
                    weight = np.log2(row['weight']*500)
                    G.add_node(node, size = weight, color = color)
                    
                for index, row in tqdm(GOPa_network.iterrows()):
                    source = row['A']
                    target = row['B']
                    color = row['color']
                    G.add_edge(source, target, color = color)
            
                
                
                # Create a pyvis Network instance
                net = Network(notebook=True, height=f"{desired_height}px", width=f"{desired_width}px")
                
                net.from_nx(G)
                
            
                net.repulsion(node_distance=150, spring_length=200)
                net.show_buttons(filter_=['nodes', 'physics'])
            
                
                net.show(os.path.join(path, 'tmp.html'))
                webbrowser.open(os.path.abspath(os.path.join(path, 'tmp.html')))
            
                
                return G
            
            else:
                print('\n \n')
                print('Lack of GO-TERM or GO-TERM is obsoleted')
        except:
            print('\n')
            print('GO-TERM not provided')
            
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



def create_netowrk_GO_static(network, width = 12, height = 10, font_size = 10):
    
    """
    This function creates a network graph in static format.

    Args:
       network (network) - network from GOPa_network_vis or show_go_term functions
       width (float) - width of the graph
       height (float) - height of the graph
       font_size (float) - size of the fonts
      
     
    Returns:
       graph: Network in static format with the legend
    """
    
    
    try:
        # Layout
        pos = nx.spring_layout(network, seed = 123)  # You can choose a different layout algorithm
    
        # Drawing nodes and edges with attributes
        node_sizes = [data['size']*10 for node, data in network.nodes(data=True)]
        node_colors = [data['color'] for node, data in network.nodes(data=True)]
        edge_colors = [data['color'] for _, _, data in network.edges(data=True)]
    
        # Create the plot
        fig, ax = plt.subplots(figsize=(width, height))
        nx.draw_networkx_nodes(network, pos, node_size=node_sizes, node_color=node_colors)
        nx.draw_networkx_edges(network, pos, edge_color=edge_colors)
    
        node_labels = {node: node for node in network.nodes()}  
        node_labels = {node: node for node in network.nodes()}  
        labels = nx.draw_networkx_labels(network, pos, labels=node_labels, font_size=font_size, font_color="black", verticalalignment='center')
       
     
        texts = [labels[node] for node in labels]
        adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', alpha=.5))
    
           
    
        plt.axis('off')  # Turn off axis
        plt.show()
        
        return fig
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def gene_interactions_network_vis(GOPa_data, GOPa_metadata, target_interaction = None, n_min = 2, top_n = 25, species = None, display_name = 'human', color = 'darkviolet', path = _path_tmp):
    
    """
    This function creates a visualization of the genes/proteins connections in the network format.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       GOPa_metadata (dict) - metadata from load_GOPa_meta function 
       target_interaction (list) - list of genes / proteins as target for interactions network display
       n_min (int) - minimal number of interactions for gene / protein
       top_n (int) - maximal number of top abundant interactions for gene / protein
       species (str) - species for gene - gene / protein - protein interaction study ['human' / 'mouse']. If None all interactions for both species.
       display_name (str) - format for gene / protein name display ['human' , 'mouse']
       color (str) - color of the nodes
       path (str) - path to temporarily save the visualization
        
       
    Returns:
       graph: Network graph for genes/proteins interactions
    """
    
    try:
        
        #screen parameter 
        
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        # Calculate desired height and width based on screen size
        desired_height = int(screen_height * 0.85)  
        desired_width = int(screen_width * 0.7)  
        
        
        #data network prepare
        
        
        GOPa_gene_interactions = pd.DataFrame(GOPa_data['GOPa_gene_interaction'])
        
        GOPa_names = pd.DataFrame(GOPa_data['gene_dictionary'])
        
        
        
        name_mapping = dict(zip(GOPa_names['dictionary_id'], GOPa_names['gene_name']))
        
        del GOPa_names
        
        
        if target_interaction != None:
            target_interaction, not_in = search_genes(target_interaction, GOPa_metadata, species=None)
            target_interaction = pd.DataFrame(target_interaction['gene_dictionary'])
            try:
                GOPa_gene_interactions = GOPa_gene_interactions[(GOPa_gene_interactions['id_1'].isin(list(target_interaction['dictionary_id']))) | (GOPa_gene_interactions['id_2'].isin(list(target_interaction['dictionary_id'])))]
                del target_interaction
            except:
                print('Genes / proteins not found in data!')
        
        
        GOPa_gene_interactions['id_1'] = GOPa_gene_interactions['id_1'].map(name_mapping)
        GOPa_gene_interactions['id_2'] = GOPa_gene_interactions['id_2'].map(name_mapping)
        

        
        if species != None and species.upper() == 'human'.upper():
           GOPa_gene_interactions = GOPa_gene_interactions[GOPa_gene_interactions['species'] == 'Homo sapiens']
        elif species != None and species.upper() == 'mouse'.upper():
           GOPa_gene_interactions = GOPa_gene_interactions[GOPa_gene_interactions['species'] == 'Mus musculus']

            
        
                
                
        if display_name != None and display_name.upper() == 'human'.upper():
            GOPa_gene_interactions['id_1'] = [x.upper() for x in GOPa_gene_interactions['id_1']]
            GOPa_gene_interactions['id_2'] = [x.upper() for x in GOPa_gene_interactions['id_2']]

        elif display_name != None and display_name.upper() == 'mouse'.upper():
            GOPa_gene_interactions['id_1'] = [x[0].upper() + x[1:].lower() for x in GOPa_gene_interactions['id_1']]
            GOPa_gene_interactions['id_2'] = [x[0].upper() + x[1:].lower() for x in GOPa_gene_interactions['id_2']]

                
           
           
        GOPa_gene_interactions = GOPa_gene_interactions[['id_1', 'id_2']].drop_duplicates()


        mx_calc = Counter(list(GOPa_gene_interactions['id_1']) + list(GOPa_gene_interactions['id_2']))
        
        mx_calc = pd.DataFrame(mx_calc.items(), columns=['gene', 'n'])
        
        mx_calc = mx_calc.sort_values(by = 'n', ascending = False)
        
        mx_calc = mx_calc.reset_index(drop = True)
        
        
      
        if len(mx_calc['n']) > top_n:
            GOPa_gene_interactions = GOPa_gene_interactions[GOPa_gene_interactions['id_1'].isin(list(mx_calc['gene'][mx_calc['n'] >= int(mx_calc['n'][top_n])]))]
            GOPa_gene_interactions = GOPa_gene_interactions[GOPa_gene_interactions['id_2'].isin(list(mx_calc['gene'][mx_calc['n'] >= int(mx_calc['n'][top_n])]))]
            
        else:
            GOPa_gene_interactions = GOPa_gene_interactions
    
        
        if len(GOPa_gene_interactions) > 0:
            
      
            
            gopa_list = list(GOPa_gene_interactions['id_1']) + list(GOPa_gene_interactions['id_2'])
           
            # Count the occurrences of each element in the list
            gopa_list = Counter(gopa_list)
            
            # Create a DataFrame from the Counter dictionary
            gopa_list = pd.DataFrame(gopa_list.items(), columns=['gene_name', 'weight'])
            
            gopa_list = gopa_list[gopa_list['weight'] >= n_min]

            GOPa_gene_interactions = GOPa_gene_interactions[GOPa_gene_interactions['id_1'].isin(list(gopa_list['gene_name']))]
            GOPa_gene_interactions = GOPa_gene_interactions[GOPa_gene_interactions['id_2'].isin(list(gopa_list['gene_name']))]
 
                
            G = nx.Graph() 
        
         
            for _, row in tqdm(gopa_list.iterrows()):
                node = row['gene_name']
                color = color
                weight = np.log2(row['weight']*500)
                G.add_node(node, size = weight, color = color)
                
            for index, row in tqdm(GOPa_gene_interactions.iterrows()):
                source = row['id_1']
                target = row['id_2']
                G.add_edge(source, target, color = 'gray')
        
            
            
            # Create a pyvis Network instance
            net = Network(notebook=True, height=f"{desired_height}px", width=f"{desired_width}px")
            
            net.from_nx(G)
            
        
            net.repulsion(node_distance=150, spring_length=200)
            net.show_buttons(filter_=['nodes', 'physics'])
        
            
            net.show(os.path.join(path, 'tmp.html'))
            webbrowser.open(os.path.abspath(os.path.join(path, 'tmp.html')))
        
            
            return G
        
        else:
            print('\n \n')
            print('Lack of interactions!')
            
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")





def gene_type_bar_plot(GOPa_data, color = 'gold', side = 'right', width = 10, bar_width = 0.5, count_type = 'p_val'):
    
    """
    This function creates a bar plot of distribution of gene types in the data

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       side (str) - orientation of bars ['left' / 'right']
       color (str)- color of the bars
       width (float) - width of the graph
       bar_width (float) - width of the bars
       count_type (str) - type of amount of term representation on bars ['perc' - percent representation / 'num' - number representation]
     
    Returns:
       graph: Distribution of gene types in the data
    """
    
    try:


        gene_info = pd.DataFrame(GOPa_data['gene_dictionary'])
        
       
        # Count the occurrences of each element in the list
        gene_info = Counter(gene_info['gen_type'])
        
        # Create a DataFrame from the Counter dictionary
        gene_info = pd.DataFrame(gene_info.items(), columns=['gene_type', 'n'])
        
        gene_info = gene_info.fillna('unknow')
        
        gene_info['%'] = gene_info['n'] / sum(gene_info['n']) * 100
        
        gene_info = gene_info.sort_values(by = 'n', ascending = False)
        
    
        height = float(len(gene_info['gene_type'])/2.5)
        
        fig, ax = plt.subplots(figsize=(width, height))
    
        # Create a horizontal bar plot
        if count_type == 'perc':
            ax.barh(gene_info['gene_type'], gene_info['%'], color=color, height = bar_width)
            ax.set_xlabel('Percent of genes [%]')
        else:
            ax.barh(gene_info['gene_type'], gene_info['n'], color=color, height = bar_width)
            ax.set_xlabel('Number of genes')
    
        # Set labels and title
       
        ax.set_ylabel('')
    
        # Invert y-axis to have names on the right
        ax.invert_yaxis()
     
    
        if side == 'right':
            ax.yaxis.tick_right()
            ax.set_yticks(range(len(gene_info)))
        elif side == 'left':
            ax.invert_xaxis()
        
       
     
                
        return fig
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")
    
    
    
def blood_level_markers_bar_plot(GOPa_data, side = 'right', color = 'red', experiment_type = 'MS', n_max = 10,  width = 10, standarize = False, bar_width = 0.5):
    
    
    """
    This function creates a bar plot of proteins level in the blood

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       side (str) - orientation of bars ['left' / 'right']
       color (str)- color of the bars
       experiment_type (str) - type of experiment used for protein level measurement in the blood ['MS' - mass spectometry / 'IM' - immuno]
       n_max (int) - maximal number of bars on the graph
       width (float) - width of the graph
       standarize (bool) - if True; standardize Concentration via calculating log(Concentration + 1), which allows you to visualize a blood gene/protein marker level if there is a very large difference between them
       bar_width (float) - width of the bars
     
    Returns:
       graph: Proteins level in the blood
    """

    try:        
        
        blood_level = pd.DataFrame(GOPa_data['GOPa_specificity']['blood_levels'])
       
       
        # Create a horizontal bar plot
        if experiment_type.upper() == 'MS':
            blood_level = blood_level[blood_level['blood_concentration_MS[pg/L]'] == blood_level['blood_concentration_MS[pg/L]']]
            blood_level = blood_level[blood_level['blood_concentration_MS[pg/L]'] != 0]

            blood_level =  blood_level.sort_values(by='blood_concentration_MS[pg/L]',  ascending = False)
            blood_level = blood_level.reset_index(drop = True)
            blood_level = blood_level.iloc[0:n_max]
            height = float(len(blood_level['gene_name'])/2.5)
            
            fig, ax = plt.subplots(figsize=(width, height))
            
            if standarize == True:
                ax.barh(blood_level['gene_name'], np.log(blood_level['blood_concentration_MS[pg/L]']+1), color=color, height = bar_width)
                ax.set_xlabel('log(Con + 1)') 
            else:
                ax.barh(blood_level['gene_name'], blood_level['blood_concentration_MS[pg/L]'], color=color, height = bar_width)
                ax.set_xlabel('Concentration [pg/L]') 
        elif experiment_type.upper() == 'IM':
            blood_level = blood_level[blood_level['blood_concentration_IM[pg/L]'] == blood_level['blood_concentration_IM[pg/L]']]
            blood_level = blood_level[blood_level['blood_concentration_IM[pg/L]'] != 0]
            blood_level =  blood_level.sort_values(by='blood_concentration_IM[pg/L]',  ascending = False)
            blood_level = blood_level.reset_index(drop = True)
            blood_level = blood_level.iloc[0:n_max]
                
            height = float(len(blood_level['gene_name'])/2.5)
            
            fig, ax = plt.subplots(figsize=(width, height))
            
            if standarize == True:
                ax.barh(blood_level['gene_name'], np.log(blood_level['blood_concentration_IM[pg/L]'] + 1), color=color, height = bar_width)
                ax.set_xlabel('log(Con + 1)')
            else:
                ax.barh(blood_level['gene_name'], blood_level['blood_concentration_IM[pg/L]'], color=color, height = bar_width)
                ax.set_xlabel('Concentration [pg/L]')

            
      
        # Set labels and title
       
        ax.set_ylabel('')
    
        # Invert y-axis to have names on the right
        ax.invert_yaxis()
     
    
        if side == 'right':
            ax.yaxis.tick_right()
            ax.set_yticks(range(len(blood_level)))
        elif side == 'left':
            ax.invert_xaxis()
        
                
        return fig
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")

    

def tissue_specificity_bar_plot(GOPa_data, p_val = 0.05, test = 'FISH', adj = 'FDR', n_max = 20, side = 'right', color = 'wheat', width = 10, bar_width = 0.5):
    
    """
    This function creates a bar plot of statistical / overrepresentation analysis of tissue specificity.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       p_val (float) - value of minimal p_val for statistical test
       test (str) - type of statistical test ['FISH' - Fisher's exact test / 'BIN' - Binomial test]
       adj (str) - type of p_value correction ['BF' - Bonferroni correction / 'FDR' - False Discovery Rate (BH procedure)]
       n_max (int) - maximal number of bars on the graph
       side (str) - orientation of bars ['left' / 'right']
       color (str)- color of the bars
       width (float) - width of the graph
       bar_width (float) - width of the bars
     
    Returns:
       graph: Bar plots of overrepresentation analysis of tissue specificity
    """

    try:
        
        
        SEQ = pd.DataFrame(GOPa_data['GOPa_specificity']['SEQ'])
       
        test_string = select_test(test, adj)
        
        
        SEQ = SEQ[SEQ[test_string] <= p_val]
        
        SEQ[test_string] = SEQ[test_string] + np.min(SEQ[test_string][SEQ[test_string] != 0])/2

        SEQ['-log(p-val)'] = -np.log(SEQ[test_string])
        
        
        SEQ = SEQ.sort_values(by = '-log(p-val)', ascending = False)
        
        SEQ = SEQ.reset_index(drop = True)

       
        SEQ = SEQ.iloc[0:n_max,:]
       
        height = float(len(SEQ['-log(p-val)'])/2.5)
        
        fig, ax = plt.subplots(figsize=(width, height))
        
        ax.barh(SEQ['name'], SEQ['-log(p-val)'], color=color, height = bar_width)
        ax.set_xlabel('-log(p-val)')
            
      
        # Set labels and title
       
        ax.set_ylabel('')
    
        # Invert y-axis to have names on the right
        ax.invert_yaxis()
     
    
        if side == 'right':
            ax.yaxis.tick_right()
            ax.set_yticks(range(len(SEQ)))
        elif side == 'left':
            ax.invert_xaxis()
        
       
     
                
        return fig
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")

    
    

def cellular_role_specificity_bar_plot(GOPa_data, p_val = 0.05, test = 'FISH', adj = 'FDR', n_max = 20, side = 'right', color = 'sandybrown', width = 10, bar_width = 0.5):
    
    """
    This function creates a bar plot of statistical / overrepresentation analysis of tissue specificity.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       p_val (float) - value of minimal p_val for statistical test
       test (str) - type of statistical test ['FISH' - Fisher's exact test / 'BIN' - Binomial test]
       adj (str) - type of p_value correction ['BF' - Bonferroni correction / 'FDR' - False Discovery Rate (BH procedure)]
       n_max (int) - maximal number of bars on the graph
       side (str) - orientation of bars ['left' / 'right']
       color (str)- color of the bars
       width (float) - width of the graph
       bar_width (float) - width of the bars
     
    Returns:
       graph: Bar plots of overrepresentation analysis of tissue specificity
    """

    try:
        
        
        location = pd.DataFrame(GOPa_data['GOPa_specificity']['location'])
       
        test_string = select_test(test, adj)
        
        
        location = location[location[test_string] <= p_val]
        
        location[test_string] = location[test_string] + np.min(location[test_string][location[test_string] != 0])/2
        
        location['-log(p-val)'] = -np.log(location[test_string])
        
        location = location.sort_values(by = '-log(p-val)', ascending = False)

        location = location.reset_index(drop = True)
       
        location = location.iloc[0:n_max,:]
       
        height = float(len(location['-log(p-val)'])/2.5)
        
        fig, ax = plt.subplots(figsize=(width, height))
        
        ax.barh(location['location'], location['-log(p-val)'], color=color, height = bar_width)
        ax.set_xlabel('-log(p-val)')
            
      
        # Set labels and title
       
        ax.set_ylabel('')
    
        # Invert y-axis to have names on the right
        ax.invert_yaxis()
     
    
        if side == 'right':
            ax.yaxis.tick_right()
            ax.set_yticks(range(len(location)))
        elif side == 'left':
            ax.invert_xaxis()
        

                
        return fig
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")

    


# get data functions


def get_gopa_results(GOPa_data):
    
    """
    This function gets the GOPa [GO-TERM, PATHWAYS, DISEASES and VIRAL-DISEASES] from GOPa_data dictionary and return in data frame.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       
     
    Returns:
       data_frame: GOPa [GO-TERM, PATHWAYS, DISEASES and VIRAL-DISEASES] 
    """
    
    try:
        
        GOPa = pd.DataFrame(copy.deepcopy(GOPa_data['GOPa']))
        return GOPa
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



def get_gene_info(GOPa_data):
    
    """
    This function gets the genes info from GOPa_data dictionary and return in data frame.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       
     
    Returns:
       data_frame: Genes info
    """
    
    try:
        
        gene_info = pd.DataFrame(copy.deepcopy(GOPa_data['gene_dictionary']))
        return gene_info
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")





def get_gopa_interactions_results(GOPa_data):
    
    """
    This function gets the GOPa interactions [GO-TERM, PATHWAYS, DISEASES and VIRAL-DISEASES] from GOPa_data dictionary and return in data frame.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       
     
    Returns:
       data_frame: GOPa interactions [GO-TERM, PATHWAYS, DISEASES and VIRAL-DISEASES] 
    """
    
    try:
        
        GOPa = pd.DataFrame(GOPa_data['GOPa'])
        GOPa_interactions = pd.DataFrame(copy.deepcopy(GOPa_data['GOPa_interactions']))
        GOPa = GOPa[['GOPa', 'relation_id']]
        GOPa = GOPa.explode('relation_id')
        GOPa = GOPa.drop_duplicates()
        name_mapping = dict(zip(GOPa['relation_id'], GOPa['GOPa']))
        GOPa_interactions['A_name'] = GOPa_interactions['A'].map(name_mapping)
        GOPa_interactions['B_name'] = GOPa_interactions['B'].map(name_mapping)
        GOPa_interactions = GOPa_interactions.drop('color', axis = 1)
        del GOPa
    
        return GOPa_interactions
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def get_gopa_gene_interaction(GOPa_data):
    
    """
    This function gets the gene interactions [IntAct, STRING] from GOPa_data dictionary and return in data frame.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       
     
    Returns:
       data_frame: Gene interactions [IntAct, STRING]
    """
    
    try:
        
        GOPa = pd.DataFrame(GOPa_data['gene_dictionary'])
        GOPa_gene_interaction = pd.DataFrame(copy.deepcopy(GOPa_data['GOPa_gene_interaction']))
        GOPa = GOPa[['gene_name', 'dictionary_id']]
    
        name_mapping = dict(zip(GOPa['dictionary_id'], GOPa['gene_name']))
        GOPa_gene_interaction['id1_name'] = GOPa_gene_interaction['id_1'].map(name_mapping)
        GOPa_gene_interaction['id2_name'] = GOPa_gene_interaction['id_2'].map(name_mapping)
        del GOPa
    
        return GOPa_gene_interaction
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def get_gopa_blood_markers(GOPa_data):

    """
    This function gets the blood markers [HPA] from GOPa_data dictionary and return in data frame.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       
     
    Returns:
       data_frame: Blood markers [HPA]
    """
    
    try:
        
        blood_levels = pd.DataFrame(copy.deepcopy(GOPa_data['GOPa_specificity']['blood_levels']))
    
        return blood_levels
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



def get_gopa_cellular_role_specificity(GOPa_data):
    
    """
    This function gets the cellular location specificity [HPA] from GOPa_data dictionary and return in data frame.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       
     
    Returns:
       data_frame: Cellular location specificity [HPA]
    """
    
    try:
        
        cellular_specificity = pd.DataFrame(copy.deepcopy(GOPa_data['GOPa_specificity']['location']))
    
        return cellular_specificity
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")


def get_gopa_tissue_specificity(GOPa_data):
    
    """
    This function gets the tissue specificity [HPA] from GOPa_data dictionary and return in data frame.

    Args:
       GOPa_data (dict) - raw GOPa_data from gopa_interaction_analysis function
       
     
    Returns:
       data_frame: Tissue specificity [HPA]
    """
    
    try:
        
        tissue_specificity = pd.DataFrame(copy.deepcopy(GOPa_data['GOPa_specificity']['SEQ']))
    
        return tissue_specificity
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")





#rnaseq functions

#visualization scatter expression

def gene_scatter(data, colors = 'viridis', species = 'human', hclust = 'complete', img_width = None, img_high = None, label_size = None, x_lab = 'Genes', legend_lab = 'log(TPM + 1)'):

        
    """
    This function creates a graph in the format of a scatter plot for expression data prepared in data frame format.
    
    Args:
       data (data frame) - data frame of genes/protein expression where on row are the gene/protein names and on column grouping variable (tissue / cell / ect. names)
       color (str) - palette color available for matplotlib in python eg. viridis
       species (str) - species for upper() or lower() letter for gene/protein name depending on 
       hclust (str) - type of data clustering of input expression data eg. complete or None if  no clustering
       img_width (float) - width of the image or None for auto-adjusting
       img_high (float) - high of the image or None for auto-adjusting
       label_size (float) - labels size of the image or None for auto-adjusting
       x_lab (str) - tex for x axis label
       legend_lab (str) - description for legend label
       
       
    Returns:
       graph: Scatter plot of expression data
    """
    
    
    try:
        scatter_df = data        

        if img_width == None:
            img_width = len(scatter_df.columns)*1.2
        
        if img_high == None:
            img_high = len(scatter_df.index)*0.9
            
        
        if label_size == None:
            label_size = np.log(len(scatter_df.index)  *  len(scatter_df.index))*2.5
            
            if label_size < 7:
                label_size = 7
        
        cm = 1/2.54
        
        if len(scatter_df) > 1:
            
           
            
        
            Z = linkage(scatter_df, method=hclust)
    
    
            # Get the order of features based on the dendrogram
            order_of_features = dendrogram(Z, no_plot=True)['leaves']
    
            indexes_sort = list(scatter_df.index)
            sorted_list_rows = []
            for n in order_of_features:
                sorted_list_rows.append(indexes_sort[n])
                
            
            
            scatter_df = scatter_df.transpose()
        
            Z = linkage(scatter_df, method=hclust)
    
            # Get the order of features based on the dendrogram
            order_of_features = dendrogram(Z, no_plot=True)['leaves']
    
            indexes_sort = list(scatter_df.index)
            sorted_list_columns = []
            for n in order_of_features:
                sorted_list_columns.append(indexes_sort[n])
                        
                   
            scatter_df = scatter_df.transpose()
            
            scatter_df = scatter_df.loc[sorted_list_rows, sorted_list_columns]
             
        scatter_df = np.log(scatter_df + 1)
        scatter_df[scatter_df <= np.mean(scatter_df.quantile(0.10))] = np.mean(np.mean(scatter_df, axis=1))/10
    
        if species.lower() == 'human':
            scatter_df.index = [x.upper() for x in scatter_df.index ]
        else:
            scatter_df.index  = [x.title() for x in scatter_df.index ]
            
        scatter_df.insert(0, '  ', 0)

        # Add a column of zeros at the end
        scatter_df[' '] = 0
             
        fig, ax = plt.subplots(figsize=(img_width*cm,img_high*cm))
    
        plt.scatter(x = [*range(0, len(scatter_df.columns), 1)], y = [' '] * len(scatter_df.columns),s=0, cmap=colors,  edgecolors=None)
    
        

    
        for index, row in enumerate(scatter_df.index):
            x = [*range(0, len(np.array(scatter_df.loc[row,])), 1)]
            y = [row] * len(x)
            s = np.array(scatter_df.loc[row,])
            plt.scatter(x,y,s=np.log(s+1)*70, c=s, cmap=colors,  edgecolors='black', vmin = np.array(scatter_df).min() ,vmax = np.array(scatter_df).max(), linewidth=0.00001)
            sm = plt.cm.ScalarMappable(cmap=colors)
            sm.set_clim(vmin = np.array(scatter_df).min() ,vmax = np.array(scatter_df).max())
            plt.xticks(x, scatter_df.columns)
            plt.ylabel(str(x_lab), fontsize=label_size)
            
            
        plt.scatter(x = [*range(0, len(scatter_df.columns), 1)], y = [''] * len(scatter_df.columns),s=0, cmap=colors,  edgecolors=None)


        
    
        plt.xticks(rotation = 80) 
        plt.tight_layout()
        plt.margins(0.005)
        plt.xticks(fontsize=label_size)
        plt.yticks(fontsize=label_size)
 
    
    
        len_bar = ax.get_position().height/5
        if len(scatter_df) < 15:
            len_bar = 0.65
            
            cbar = plt.colorbar(sm)
            cbar.ax.set_ylabel(str(legend_lab), fontsize=label_size*0.9)
            cbar.ax.yaxis.set_ticks_position('right')
            cbar.ax.set_position([ax.get_position().x1 + 0.05, (ax.get_position().y0 + ax.get_position().y1)/1.9 , ax.get_position().width/0.05, len_bar])
            cbar.ax.yaxis.set_label_position('right')
            cbar.ax.yaxis.set_tick_params(labelsize=label_size*0.8)
            cbar.outline.set_edgecolor('none')
        else:
            cbar = plt.colorbar(sm)
            cbar.ax.set_ylabel(str(legend_lab), fontsize=label_size*0.9)
            cbar.ax.yaxis.set_ticks_position('right')
            cbar.ax.set_position([ax.get_position().x1 + 0.05, (ax.get_position().y0 + ax.get_position().y1)/1.45 , ax.get_position().width/0.05, len_bar])
            cbar.ax.yaxis.set_label_position('right')
            cbar.ax.yaxis.set_tick_params(labelsize=label_size*0.8)
            cbar.outline.set_edgecolor('none')
    
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)     
        ax.xaxis.set_tick_params(length=0,labelbottom=True)
        ax.yaxis.set_tick_params(length=0,labelbottom=True)
        ax.grid(False)
    
    
        return fig
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")


#preapre rnaseq

def gene_specificity(gene_list, path_in_use = _path_in_inside):
    
    """
    This function creates a dictionary of RNA-SEQ data for studied genes.
    
    Args:
       gene_list (list) - list of genes to check in the context of rna-seq data 

       
    Returns:
       dictionary: Dictionary of RNA-SEQ data for studied genes
    """
    
    try:
        
        print('Genes search start...')
        
        with open(path_in_use + '/GOPa_metadata_dict.json', 'r') as json_file:
            GOPa_metadata = (json.load(json_file))
            
            
        GOPa_data, not_found = search_genes(gene_list, GOPa_metadata, species='human')
        
        GOPa_genes = list(GOPa_data['gene_dictionary']['gene_name'])
        
        del GOPa_metadata, GOPa_data
    
        print('RNA-SEQ data searching...')
            
        with open(path_in_use + '/human_tissue_expression_fetal_development_circular.json', 'r') as json_file:
            human_tissue_expression_fetal_development_circular = (json.load(json_file))
            
        human_tissue_expression_fetal_development_circular = pd.DataFrame.from_dict(dict({k:v for k,v in human_tissue_expression_fetal_development_circular.items() if k != 'tissue'}), orient='index',  columns = human_tissue_expression_fetal_development_circular['tissue'])
        human_tissue_expression_fetal_development_circular = human_tissue_expression_fetal_development_circular.loc[[x for x in GOPa_genes if x in human_tissue_expression_fetal_development_circular.index], :]
    
        with open(path_in_use + '/human_tissue_expression_HPA.json', 'r') as json_file:
            human_tissue_expression_HPA = (json.load(json_file))
            
        human_tissue_expression_HPA = pd.DataFrame.from_dict(dict({k:v for k,v in human_tissue_expression_HPA.items() if k != 'tissue'}), orient='index',  columns = human_tissue_expression_HPA['tissue'])
        human_tissue_expression_HPA = human_tissue_expression_HPA.loc[[x for x in GOPa_genes if x in human_tissue_expression_HPA.index], :]
        
        
        with open(path_in_use + '/human_tissue_expression_illumina_bodyMap2.json', 'r') as json_file:
            human_tissue_expression_illumina_bodyMap2 = (json.load(json_file))
            
        human_tissue_expression_illumina_bodyMap2 = pd.DataFrame.from_dict(dict({k:v for k,v in human_tissue_expression_illumina_bodyMap2.items() if k != 'tissue'}), orient='index',  columns = human_tissue_expression_illumina_bodyMap2['tissue'])
        human_tissue_expression_illumina_bodyMap2 = human_tissue_expression_illumina_bodyMap2.loc[[x for x in GOPa_genes if x in human_tissue_expression_illumina_bodyMap2.index], :]
    
    
        with open(path_in_use + '/human_tissue_expression_RNA_total_tissue.json', 'r') as json_file:
            human_tissue_expression_RNA_total_tissue = (json.load(json_file))
            
        human_tissue_expression_RNA_total_tissue = pd.DataFrame.from_dict(dict({k:v for k,v in human_tissue_expression_RNA_total_tissue.items() if k != 'tissue'}), orient='index',  columns = human_tissue_expression_RNA_total_tissue['tissue'])
        human_tissue_expression_RNA_total_tissue = human_tissue_expression_RNA_total_tissue.loc[[x for x in GOPa_genes if x in human_tissue_expression_RNA_total_tissue.index], :]
    
        seq_dict = {'human_tissue_expression_fetal_development_circular':human_tissue_expression_fetal_development_circular,
                    'human_tissue_expression_HPA':human_tissue_expression_HPA,
                    'human_tissue_expression_illumina_bodyMap2':human_tissue_expression_illumina_bodyMap2,
                    'human_tissue_expression_RNA_total_tissue':human_tissue_expression_RNA_total_tissue}
        
        return seq_dict
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")




def rna_seq_scatter(rna_seq):
    
      
    """
    This function creates a ditionary of graphs for RNA-SEQ data from gene_specificity function
    
    Args:
       rna_seq (dictionary) - data from gene_specificity function
       
    Returns:
       dictionary: Dictionary of graphs for different type of RNA-SEQ data for different tissue specificity
    """
    
    try:
        
        image_dict = {}
        for k in rna_seq.keys():
            print('Preparing graph for ' + str(k))
            
            
            image_dict[k] =gene_scatter(rna_seq[k], colors = 'viridis', species = 'human', hclust = 'complete', img_width = None, img_high = None, label_size = None)
    
        return image_dict
    
    except:
        print('\n')
        print("Something went wrong. Check the function input data and try again!")



#Deregulated GOPa function - compare two genes / proteins list 


def DGOPa(gene_up, gene_down, GOPa_metadata, species = None, min_fc = 0.5, p_val = 0.05, test = 'FISH', adj = 'FDR'):
    
    """
    This function conducts full GOPa analysis on two gene / protein lists [gene_up, gene_down] including search_genes, gopa_analysis, gopa_interaction_analysis, and gopa_specificity_analysis.
    This function is useful when you have to compare two sides genes / proteins deregulations (upregulated vs. downregulated) and choose the most accurate results adjusted to the provided gene lists based on min_fc (minimal fold change) between GOPa projects.

    Args:
       gene_up (list)- list of genes eg. ['KIT', 'EDNRB', 'PAX3'] 
       gene_down (list)- list of genes eg. ['KIT', 'EDNRB', 'PAX3'] 
       GOPa_metadata (dict) - metadata from load_GOPa_meta function 
       species (str or None) - ['human' / 'mouse' / 'both' / None] 
       min_fc (float) - minimal value of fold change the normalized by number of genes in analysis results of GOPa between GOPa projects obtained from the provided lists of genes [gene_up / gene_down]
       p_val (float) - value of minimal p_val for statistical test
       test (str) - type of statistical test ['FISH' - Fisher's exact test / 'BIN' - Binomial test]
       adj (str) - type of p_value correction ['BF' - Bonferroni correction / 'FDR' - False Discovery Rate (BH procedure)]
       
       If choose 'human' or 'mouse' you will obtain information about this species' genes. 
       If choose 'both' you will obtain information for genes that are available mutually for both species. 
       If choose None you will obtain information for all genes available in the metadata.       

    Returns:
       list of dict: A list of two dictionaries with analyzed GOPa projects obtained on the provided list of genes [gene_up, gene_down] corrected on specific occurrences in GOPa results with min_fc. The first dictionary is related to gene_up results and the second to gene_down results 
       
    """
    
    test_string = select_test(test, adj)


    GOPa_data_up, not_found = search_genes(gene_up, GOPa_metadata, species=species)
     
    
    GOPa_data_up =  gopa_analysis(GOPa_data_up, GOPa_metadata)
    
      
    GOPa_data_up =  gopa_interaction_analysis(GOPa_data_up)
    
    GOPa_data_up =  gopa_specificity_analysis(GOPa_data_up, GOPa_metadata)


    
    GOPa_data_down, not_found = search_genes(gene_down, GOPa_metadata, species=species)
     
    
    GOPa_data_down =  gopa_analysis(GOPa_data_down, GOPa_metadata)
    
      
    GOPa_data_down =  gopa_interaction_analysis(GOPa_data_down)
    
    
    GOPa_data_down =  gopa_specificity_analysis(GOPa_data_down, GOPa_metadata)

    
    #GOPa

    GOPa_up = pd.DataFrame(GOPa_data_up['GOPa'])
    GOPa_up = GOPa_up[GOPa_up[test_string] <= p_val]
    GOPa_up['norm_n'] =  GOPa_up['n'] / len(gene_up)
    
    
    GOPa_down = pd.DataFrame(GOPa_data_down['GOPa'])
    GOPa_down = GOPa_down[GOPa_down[test_string] <= p_val]
    GOPa_down['norm_n'] =  GOPa_down['n'] / len(gene_down)
    
    
    gopa_down_list = []
    for g in GOPa_down['GOPa']:
        if g in list(GOPa_up['GOPa']):
            if(float(GOPa_down['norm_n'][GOPa_down['GOPa'] == g])/ float(GOPa_up['norm_n'][GOPa_up['GOPa'] == g]) >= min_fc):
                gopa_down_list.append(g)
        else:
            gopa_down_list.append(g)
        
            
    gopa_up_list = []
    for g in GOPa_up['GOPa']:
        if g in list(GOPa_down['GOPa']):
            if(float(GOPa_up['norm_n'][GOPa_up['GOPa'] == g])/ float(GOPa_down['norm_n'][GOPa_down['GOPa'] == g]) >= min_fc):
                gopa_up_list.append(g)
        else:
            gopa_up_list.append(g)
            
            
    GOPa_down = GOPa_down[GOPa_down['GOPa'].isin(gopa_down_list)]
    GOPa_data_down['GOPa'] = GOPa_down.to_dict(orient = 'list')
    
    GOPa_up = GOPa_up[GOPa_up['GOPa'].isin(gopa_down_list)]
    GOPa_data_up['GOPa'] = GOPa_up.to_dict(orient = 'list')
    
    #specificity
    
    
    GOPa_up = pd.DataFrame(GOPa_data_up['GOPa_specificity']['SEQ'])
    GOPa_up = GOPa_up[GOPa_up[test_string] <= p_val]
    GOPa_up['norm_n'] =  GOPa_up['n'] / len(gene_up)
    
    
    GOPa_down = pd.DataFrame(GOPa_data_down['GOPa_specificity']['SEQ'])
    GOPa_down = GOPa_down[GOPa_down[test_string] <= p_val]
    GOPa_down['norm_n'] =  GOPa_down['n'] / len(gene_down)
    
    
    gopa_down_list = []
    for g in GOPa_down['name']:
        if g in list(GOPa_up['name']):
            if(float(GOPa_down['norm_n'][GOPa_down['name'] == g])/ float(GOPa_up['norm_n'][GOPa_up['name'] == g]) >= min_fc):
                gopa_down_list.append(g)
        else:
            gopa_down_list.append(g)
        
    gopa_up_list = []
    for g in GOPa_up['name']:
        if g in list(GOPa_down['name']):
            if(float(GOPa_up['norm_n'][GOPa_up['name'] == g])/ float(GOPa_down['norm_n'][GOPa_down['name'] == g]) >= min_fc):
                gopa_up_list.append(g)
        else:
            gopa_up_list.append(g)
            
            
    GOPa_down = GOPa_down[GOPa_down['name'].isin(gopa_down_list)]
    GOPa_data_down['GOPa_specificity']['SEQ'] = GOPa_down.to_dict(orient = 'list')
    
    GOPa_up = GOPa_up[GOPa_up['name'].isin(gopa_down_list)]
    GOPa_data_up['GOPa_specificity']['SEQ'] = GOPa_up.to_dict(orient = 'list')
    
    
    #location
    
    
    GOPa_up = pd.DataFrame(GOPa_data_up['GOPa_specificity']['location'])
    GOPa_up = GOPa_up[GOPa_up[test_string] <= p_val]
    GOPa_up['norm_n'] =  GOPa_up['n'] / len(gene_up)
    
    
    GOPa_down = pd.DataFrame(GOPa_data_down['GOPa_specificity']['location'])
    GOPa_down = GOPa_down[GOPa_down[test_string] <= p_val]
    GOPa_down['norm_n'] =  GOPa_down['n'] / len(gene_down)
    
    
    
    gopa_down_list = []
    for g in GOPa_down['location']:
        if g in list(GOPa_up['location']):
            if(float(GOPa_down['norm_n'][GOPa_down['location'] == g])/ float(GOPa_up['norm_n'][GOPa_up['location'] == g]) >= min_fc):
                gopa_down_list.append(g)
        else:
            gopa_down_list.append(g)
      
            
    gopa_up_list = []
    for g in GOPa_up['location']:
        if g in list(GOPa_down['location']):
            if(float(GOPa_up['norm_n'][GOPa_up['location'] == g])/ float(GOPa_down['norm_n'][GOPa_down['location'] == g]) >= min_fc):
                gopa_up_list.append(g)
        else:
            gopa_up_list.append(g)
            
            
    GOPa_down = GOPa_down[GOPa_down['location'].isin(gopa_down_list)]
    GOPa_data_down['GOPa_specificity']['location'] = GOPa_down.to_dict(orient = 'list')
    
    GOPa_up = GOPa_up[GOPa_up['location'].isin(gopa_down_list)]
    GOPa_data_up['GOPa_specificity']['location'] = GOPa_up.to_dict(orient = 'list')
    
    
    return GOPa_data_up, GOPa_data_down
