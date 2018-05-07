import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn import preprocessing
from scipy import sparse
from operator import itemgetter
# from scipy.spatial.distance import cosine
import pickle
# import seaborn
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
# import os
from datetime import datetime
def vectorizer(columnsValues):
    # location,service,certification,age_prefernce,gender,types,availability,
    #           wage_preference,exprience,clients_attended,doorstep_service,
    #           reference,liscenced,shopping_liscence
    vector = []
    location = [0] * 44
    occupatn = [0] * 23
    cert = [0] * 2
    age = [0] * 4
    gender = [0] * 2
    types = [0] * 2
    availability = [0] * 4
    minimumWage = [0] * 3
    exp = [0] * 3
    clients = [0] * 5
    references = [0] * 2
    liscenced = [0] * 2
    shoppingliscence = [0] * 2
    doorstepService = [0] * 2

    location[int(columnsValues[2])] = 1
    occupatn[int(columnsValues[3])] = 1
    cert[int(columnsValues[4])] = 1
    age[int(columnsValues[5])] = 1
    gender[int(columnsValues[6])] = 1
    types[int(columnsValues[7])] = 1
    availability[int(columnsValues[8])] = 1
    minimumWage[int(columnsValues[9])] = 1
    exp[int(columnsValues[10])] = 1
    clients[int(columnsValues[11])] = 1
    doorstepService[int(columnsValues[12])] = 1
    references[int(columnsValues[13])] = 1
    liscenced[int(columnsValues[14])] = 1
    shoppingliscence[int(columnsValues[15])] = 1

    vector.extend(location)
    vector.extend(occupatn)
    vector.extend(cert)
    vector.extend(age)
    vector.extend(gender)
    vector.extend(types)
    vector.extend(availability)
    vector.extend(minimumWage)
    vector.extend(exp)
    vector.extend(clients)
    vector.extend(doorstepService)
    vector.extend(references)
    vector.extend(liscenced)
    vector.extend(shoppingliscence)
    return list(vector)


class BuildAndTrain():

    def __init__(self):
        """Calls dataUtility utitlities functions"""
        self.start_time = datetime.now()
        self.df = self.dataUtility()
        self.classesOfColumns = defaultdict(list)
        self.occupations = defaultdict(list)
        self.kmeans = []
        self.df = self.utilities(self.df)
        # print('utilities called!!')
        # self.kneighborsOfUserQuery, self.finalCluster = self.KmeanPredictor('1', sparse1[116])
        self.classesOfColumns = self.unpickleLoader('clsofclos')
        self.occupations = self.unpickleLoader('occupations')
        # print(self.occupations.keys())
    
    
    def pickler(self, toBeDumped, filename):
        """A helper function to pickle data"""
        with open(str(filename) + '.pkl', 'wb') as file:
            file.write(pickle.dumps(toBeDumped))

    def unpickleLoader(self,filename):
        """A helper function to unpickle data"""
        with open(filename + '.pkl', 'rb') as f:
            unpickled = pickle.loads(f.read())
        return unpickled
    
    def dataUtility(self):
        """Reads the main input csv in a dataframe for computation"""
        df = pd.read_csv('final_data.csv')
        df = df.drop(['id', 'availabilityPreference', 'aadharCard'],
                     axis=1)
        df.dropna(inplace=True)
        # print('DataUtility Done')
        return df

    def classer(self, temp_df):
        """Groups age, experience, clientsAttended information"""
        temp_df.loc[temp_df['minimumWage']<5001, 'minimumWage'] = 0
        temp_df.loc[np.logical_and(temp_df['minimumWage']>5000, temp_df['minimumWage']<8001),'minimumWage'] = 1
        temp_df.loc[np.logical_and(temp_df['minimumWage']>8000, temp_df['minimumWage']<10001),'minimumWage'] = 2

        temp_df.loc[(temp_df['experience']<3), 'experience'] = 0
        temp_df.loc[np.logical_and(temp_df['experience']>2, temp_df['experience']<7),'experience'] = 1
        temp_df.loc[np.logical_and(temp_df['experience']>6, temp_df['experience']<11),'experience'] = 2

        temp_df.loc[temp_df['age']<21,'age'] = 0
        temp_df.loc[np.logical_and(temp_df['age']>20, temp_df['age']<26),'age'] = 1
        temp_df.loc[np.logical_and(temp_df['age']>25, temp_df['age']<30),'age'] = 2
        temp_df.loc[np.logical_and(temp_df['age']>29, temp_df['age']<41),'age'] = 3

        temp_df.loc[temp_df['clientsAttended']<11, 'clientsAttended'] = 0
        temp_df.loc[np.logical_and(temp_df['clientsAttended']>10, temp_df['clientsAttended']<21),'clientsAttended'] = 1
        temp_df.loc[np.logical_and(temp_df['clientsAttended']>20, temp_df['clientsAttended']<31),'clientsAttended'] = 2
        temp_df.loc[np.logical_and(temp_df['clientsAttended']>30, temp_df['clientsAttended']<41),'clientsAttended'] = 3
        temp_df.loc[temp_df['clientsAttended']>40, 'clientsAttended'] = 4
        return temp_df
    
    def classes_maker(self,temp_df):
        """Label encoding for all non numeric data and returns new df"""
        temp = temp_df.columns.tolist()
        temp.remove('phoneNo')
        for i in temp:
            le = preprocessing.LabelEncoder()
            le.fit(temp_df[i])
            self.classesOfColumns[i].append(le.classes_)
            temp_df[i] = le.transform(temp_df[i])
        # print(temp_df.columns)
        return temp_df
    
    def all_occupations_in_a_location(self, temp_df):
        """Finds all the workers at all locations and store it in dict with key as\
        occupation and value as list of indexes"""
        # print('Sorting workers')
        for index, row in temp_df.iterrows():
            self.occupations[row['occupation']].append(index)

        for key, values in self.occupations.items():
            t_set = list(set(values))
            self.occupations[key] = t_set
        # print(self.occupations.keys())
        
    def occs_splitter(self, df):
        """Splits data into multiple datasets w.r.t occupation and stores it in a  seperate\
            csv file"""
        # print('Splitting data.....')
        for key in self.occupations.keys():
            temp_df = df.iloc[self.occupations[key]]
            # temp_df.loc[:, ~df.columns.str.contains('^Unnamed')]
            temp_df.to_csv(str(key) + '.csv', index=False)
    
    
    def sparser(self):
        """Generate sparse matrix of the splitted data and pickles the matrix"""
        # print('Generating sparse matrix for data...')
        for i in range(len(self.occupations.keys())):
            sparse = []
            temp_df = pd.read_csv(str(i)+'.csv')

            for index, row in temp_df.iterrows():
                vector           = []
                location         = [0] * np.unique(self.df['location'])
                occupatn         = [0] * np.unique(self.df['occupation'])
                cert             = [0] * np.unique(self.df['certification'])
                age              = [0] * np.unique(self.df['age'])
                gender           = [0] * np.unique(self.df['gender'])
                types            = [0] * np.unique(self.df['type'])
                availability     = [0] * np.unique(self.df['availability'])
                minimumWage      = [0] * np.unique(self.df['minimumWage'])
                exp              = [0] * np.unique(self.df['experience'])
                clients          = [0] * np.unique(self.df['clientsAttended'])
                references       = [0] * np.unique(self.df['references'])
                liscenced        = [0] * np.unique(self.df['liscenced'])
                shoppingliscence = [0] * np.unique(self.df['shoppingliscence'])
                doorstepService  = [0] * np.unique(self.df['doorstepService '])

                location[row['location']] = 1
                occupatn[row['occupation']] = 1
                cert[row['certification']] = 1
                age[row['age']] = 1
                gender[row['gender']] = 1
                types[row['type']] = 1
                availability[row['availability']] = 1
                minimumWage[row['minimumWage']] = 1
                exp[row['experience']] = 1
                clients[row['clientsAttended']] = 1
                doorstepService[row['doorstepService ']] = 1
                references[row['references']] = 1
                liscenced[row['liscenced']] = 1
                shoppingliscence[row['shoppingliscence']] = 1

                vector.extend(location)
                vector.extend(occupatn)
                vector.extend(cert)
                vector.extend(age)
                vector.extend(gender)
                vector.extend(types)
                vector.extend(availability)
                vector.extend(minimumWage)
                vector.extend(exp)
                vector.extend(clients)
                vector.extend(doorstepService)
                vector.extend(references)
                vector.extend(liscenced)
                vector.extend(shoppingliscence)
                sparse.append(list(vector))
            self.pickler(sparse, str(i)+'_sparse')
    
    def utilities(self, temp_df):
        """Calls multiple utilities and return the result dataframe"""
        # print('Executing utilities functions ....')
        # temp_df = self.classer(temp_df)
        # temp_df = self.classes_maker(temp_df)
        # self.all_occupations_in_a_location(temp_df)
        # self.occs_splitter(temp_df)
        # self.sparser()
        # self.pickler(self.classesOfColumns, 'clsofclos')
        # self.pickler(self.occupations, 'occupations')
        # print("Utilites executed")
        return temp_df
    
    def modelling(self, service, userquery):
        """Creates a Kmean model and starts ml processes in cascade"""
        # print('Generating model ...')
        temp_files = []
        for i in range(len(self.occupations.keys())):
            temp_files.append(self.unpickleLoader(str(i)+'_sparse'))
            kmodel = KMeans(max_iter=4,
                            n_clusters=10, n_init=10).fit(temp_files[i])
            self.kmeans.append(kmodel)
            # self.pickler(kmodel, str(i) + '_model')
        # print('Modelling done')
        return self.KmeanPredictor(service, userquery)
    
    def KmeanPredictor(self,service, userquery): # modelNos same as service
        """Predicts the cluster in which user query belongs to"""
        kmeanModel = self.unpickleLoader(str(service) + '_model')
        # print('Predicting kmean cluster')
        return self.KMeanClusterIndexes(kmeanModel, kmeanModel.predict(np.array(userquery).reshape(1,-1)), userquery, service)
    
    
    def KMeanClusterIndexes(self, kMeanModel, userQueryClusterLabel, userquery, service):
        """Get all the data points in the user query cluster"""
        temp = kMeanModel.labels_.tolist()
        count = 0
        li = []
        for i in temp:
            if i == userQueryClusterLabel:
                li.append(count)
            count = count + 1
        # print('getting all points in the same cluster')
        return self.clusteredDataframe(li, service, userquery)
    
    def clusteredDataframe(self, clustEleIndex, service, userQuery):
        """Process the data in the clustered dataframe"""
        temp_sparse = self.unpickleLoader(str(service) + '_sparse')
        temp_df = pd.read_csv(str(service) + '.csv')
        KMclustered_dataframe = temp_df.loc[clustEleIndex]
        temp_sparse = [temp_sparse[x] for x in clustEleIndex]
        # print('Temporary cluster formation')
        return self.NearestNeighborsAlgo(temp_sparse, userQuery,KMclustered_dataframe)
    
    def NearestNeighborsAlgo(self, clusteredSparse, userQuery, KMeanClusterIndexes):
        """Apply KNN to the clustered dataframe"""
        neigh = NearestNeighbors(n_neighbors=15)
        neigh.fit(clusteredSparse)
        # print('Applying nearest neighbour')
        print("Total time: ", datetime.now() - self.start_time)
        return neigh.kneighbors(np.array(userQuery).reshape(1,-1)), KMeanClusterIndexes


# kmeans = []
# if __name__ == '__main__':
#     bnt = BuildAndTrain()

#     df = bnt.dataUtility()
#     classesOfColumns = defaultdict(list)
#     occupations = defaultdict(list)

# #     pickler(classesOfColumns, 'clsofclos')
# #     pickler(occupations, 'occupations')
#     df = bnt.utilities(df)
#     # sparse1 = bnt.unpickleLoader('1_sparse')
#     kneighborsOfUserQuery, finalCluster = bnt.modelling('1', sparse1[116])
#     print(kneighborsOfUserQuery, finalCluster)
