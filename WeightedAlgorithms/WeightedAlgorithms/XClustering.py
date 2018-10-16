class XClustering(object):
        
        def __init__(self):


	def Weighted_Kmeans(self,P_C,N_Clusters,W,Force_Fit): 
            Var_Mean=Var_STD=P_C.describe().T
            Var_Mean=Var_Mean['mean']
            Var_STD=Var_STD['std']
            Var_STD=Var_STD.reset_index()
            Var_Mean=Var_Mean.reset_index()
            Var_Mean=Var_Mean.merge(Var_STD,on='index')
            del Var_STD

            i=1
            while(i<N_Clusters) :   

                new_col_1="Points_Above_"+str(i)
                new_col_2="Points_Below_"+str(i)

                x=Var_Mean['mean']+(Var_Mean['std']*i)
                Var_Mean[new_col_1]=x
                x=Var_Mean['mean']-(Var_Mean['std']*i)
                Var_Mean[new_col_2]=x

                i=i+1

            del Var_Mean['std']  
            colname_list=['index']
            for i in range(1,len(Var_Mean.columns)):
                colname_list=colname_list+[("C"+str(i))]

            Var_Mean.columns=colname_list
            Var_Mean=Var_Mean.ix[Var_Mean['index']!='index'] 
            Var_Mean=Var_Mean.ix[:,0:N_Clusters+1]
            

            Iteration_Error_Value={}
            iteration_count=0
            Prev_ITR_ERROR=99999999*100000
            Current_ITR_ERROR=0

            while(Current_ITR_ERROR<Prev_ITR_ERROR):
                iteration_count=iteration_count+1
                Error_Value=0
                Distance_Dict={}
                for row_index in range(0,len(P_C)):
                    T_DF=pd.DataFrame(P_C.ix[row_index]).reset_index().merge(Var_Mean,on='index')
                    T_DF.rename(columns={row_index: 'Point'}, inplace=True)


                    if Force_Fit==True:
                        for c_n in range(0,N_Clusters):
                            c_n=c_n+1

                            Col_Name="C"+str(c_n)
                            New_Col_Name=Col_Name+'_Diff'

                            T_DF[New_Col_Name]=W*((T_DF['Point']-T_DF[Col_Name])*(T_DF['Point']-T_DF[Col_Name]))
                    else:
                        Col_2b_diffed=list(Var_Mean.columns)
                        Col_2b_diffed.remove('index')

                        for Col_Name in Col_2b_diffed:
                            New_Col_Name=Col_Name+'_Diff'
                            T_DF[New_Col_Name]=W*((T_DF['Point']-T_DF[Col_Name])*(T_DF['Point']-T_DF[Col_Name]))



                    T_DF['W']=W

                    matching = [s for s in list(T_DF.columns) if "_Diff" in s]


                    Distance_Dict[row_index]=(T_DF[matching].sum()).to_dict()
                    Distance_Dict[row_index].update({'Nearest': ((T_DF[matching].sum())).idxmin().replace('_Diff','')})
                    Error_Value=Error_Value+(T_DF[matching].sum()).min()

                Distance_DF=pd.DataFrame.from_dict(Distance_Dict, orient='index')
                Iteration_Error_Value[iteration_count]=Error_Value

                P_C['index']=P_C.index
                Distance_DF['index']=Distance_DF.index
                Distance_DF=Distance_DF.drop(columns=matching)


                New_Points=P_C.merge(Distance_DF,on='index')
                del New_Points['index']
                
            
                colname_list=['index']
                
                for i in range(1,N_Clusters+1):
                    colname_list=colname_list+[("C"+str(i))]
                Temp_Var_Mean=pd.DataFrame(New_Points.groupby(['Nearest']).mean().T).reset_index()

                Missing_Clusters=list(set(colname_list)-set(Temp_Var_Mean.columns))
                
                if Force_Fit==True:                
                    for i in range(0,len(Missing_Clusters)):
                        New_Points['Nearest'][i]=Missing_Clusters[i]

                
                Var_Mean=pd.DataFrame(New_Points.groupby(['Nearest']).mean().T).reset_index()
   
                print ("Iteration : " +str(iteration_count)+" Error Value : "+str(Error_Value.round(2)))

                if(iteration_count==1):
                    Current_ITR_ERROR=Error_Value
                    Prev_ITR_ERROR=99999999*100000
                else:
                    Prev_ITR_ERROR=Current_ITR_ERROR
                    Current_ITR_ERROR=Error_Value
                    
                    
            return New_Points


