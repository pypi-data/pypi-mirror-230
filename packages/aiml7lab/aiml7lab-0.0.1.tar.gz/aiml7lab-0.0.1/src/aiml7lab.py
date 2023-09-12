def pg1a():
    """
    1. Write a program to implement k-Nearest Neighbour algorithm to classify the iris data set. Print both correct and wrong predictions.
    """
    print(r"""  
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

# Load iris dataset
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train and classify using k-nearest neighbors
k = 3
knn = KNeighborsClassifier(n_neighbors=k)
knn.fit(X_train, y_train)
predictions = knn.predict(X_test)

# Print correct and wrong predictions
for i in range(len(y_test)):
    if predictions[i] == y_test[i]:
        print(f"Correct prediction: {X_test[i]} is class {predictions[i]}")
    else:
        print(f"Wrong prediction: {X_test[i]} is classified as {predictions[i]}, expected {y_test[i]}")
    """)
    
def pg1b():
    """
    1. Write a program to implement k-Nearest Neighbour algorithm to classify the iris data set. Print both correct and wrong predictions. 
    Java/Python ML library classes can be used for this problem.
    """
    print(r"""  
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from sklearn.model_selection import train_test_split
iris_dataset=load_iris()
X_train,X_test,Y_train,Y_test=train_test_split(iris_dataset["data"],iris_dataset["target"],random_state=0)
kn=KNeighborsClassifier(n_neighbors=1)
kn.fit(X_train,Y_train)
print("\nActual and Predicted values for testsets \n")
for i in range(len(X_test)):
    x=X_test[i]
    x_new=np.array([x])
    prediction=kn.predict(x_new)
    print("\nActual :{0}{1},predicted:{2}{3}".format(Y_test[i],iris_dataset["target_names"][[Y_test[i]]],prediction,iris_dataset["target_names"][prediction]))
    print("\nTest score[Accuracy]:{:.2f}\n".format(kn.score(X_test,Y_test)))
    """)

def pg1c():
    """
    1. Write a program to implement k-Nearest Neighbour algorithm to classify the iris data set. Print both correct and wrong predictions. 
    Java/Python ML library classes can be used for this problem.
    """
    print(r"""
from sklearn.model_selection import train_test_split 
from sklearn.neighbors import KNeighborsClassifier 
from sklearn import datasets
iris=datasets.load_iris() 
print("Iris Data set loaded...")
x_train, x_test, y_train, y_test = train_test_split(iris.data,iris.target,test_size=0.1)
#random_state=0
for i in range(len(iris.target_names)):
    print("Label", i , "-",str(iris.target_names[i]))
classifier = KNeighborsClassifier(n_neighbors=5)
classifier.fit(x_train, y_train)
y_pred=classifier.predict(x_test)
print("Results of Classification using K-nn with K=5 ") 
for r in range(0,len(x_test)):
    print(" Sample:", str(x_test[r]), " Actual-label:", str(y_test[r])," Predicted-label:", str(y_pred[r]))
    print("Classification Accuracy :" , classifier.score(x_test,y_test));
    """)

def pg2a():
    """
    2. Develop a program to apply K-means algorithm to cluster a set of data stored in .CSV file. 
    Use the same data set for clustering using EM algorithm. Compare the results of these two algorithms and comment on the quality of clustering.
    """
    print(r"""
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture

# Read data from .csv file
data = pd.read_csv('data.csv')

# Apply k-means clustering
kmeans = KMeans(n_clusters=3)
kmeans.fit(data)
kmeans_labels = kmeans.predict(data)

# Apply EM algorithm clustering
em = GaussianMixture(n_components=3)
em.fit(data)
em_labels = em.predict(data)

# Compare the results of k-means and EM algorithm clustering
kmeans_score = kmeans.score(data)
em_score = em.score(data)
print("K-means clustering score:", kmeans_score)
print("EM algorithm clustering score:", em_score)
    """)
    
def pg2b():
    """
    2. Apply EM algorithm to cluster a set of data stored in a .CSV file. Use the same data set for
    clustering using k-Means algorithm. Compare the results of these two algorithms and comment
    on the quality of clustering. You can add Java/Python ML library classes/API in the program.
    """
    print(r"""
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import KMeans
import sklearn.metrics as sm
from sklearn import preprocessing 
from sklearn.mixture import GaussianMixture
import pandas as pd
import numpy as np

iris = datasets.load_iris()
X = pd.DataFrame(iris.data)
X.columns = ['Sepal_Length','Sepal_Width','Petal_Length','Petal_Width']

y = pd.DataFrame(iris.target)
y.columns = ['Targets']

model = KMeans(n_clusters=3)
model.fit(X)

score1=sm.accuracy_score(y, model.labels_)
print("Accuracy of KMeans=",score1)

plt.figure(figsize=(7,7))
colormap = np.array(['red', 'lime', 'black'])
plt.subplot(1, 2, 1) 
plt.scatter(X.Petal_Length, X.Petal_Width, c=colormap[model.labels_], s=40)
plt.title('K Mean Classification')

scaler = preprocessing.StandardScaler()
scaler.fit(X)
xsa = scaler.transform(X)

xs = pd.DataFrame(xsa, columns = X.columns)
gmm = GaussianMixture(n_components=3)
gmm.fit(xs)                 
y_cluster_gmm = gmm.predict(xs)  
                                                                  
score2=sm.accuracy_score(y, y_cluster_gmm)
print("Accuracy of EM=",score2)
plt.subplot(1, 2, 2)
plt.scatter(X.Petal_Length, X.Petal_Width, c=colormap[y_cluster_gmm], s=40)
plt.title('EM Classification')
    """)

def pg2c():
    """
    2. Develop a program to apply K-means algorithm to cluster a set of data stored in .CSV file. 
    Use the same data set for clustering using EM algorithm. Compare the results of these two algorithms and comment on the quality of clustering.
    """
    print(r"""
#	Kmeans 	
from sklearn import datasets 
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split

iris = datasets.load_iris() 
print(iris)
X_train,X_test,y_train,y_test = train_test_split(iris.data,iris.target) 
model =KMeans(n_clusters=3)
model.fit(X_train,y_train) 
model.score
print('K-Mean: ',metrics.accuracy_score(y_test,model.predict(X_test)))

#-------Expectation and Maximization----------
from sklearn.mixture import GaussianMixture 
model2 = GaussianMixture(n_components=3) 
model2.fit(X_train,y_train)
model2.score
print('EM Algorithm:',metrics.accuracy_score(y_test,model2.predict(X_test)))
    """)

def pg3a():
    """
    3. Implement the non-parametric Locally Weighted Regressionalgorithm in order to fit data points. Select appropriate data set for your experiment and draw graphs
    """
    print(r"""
import numpy as np
import matplotlib.pyplot as plt

# Selecting appropriate dataset
X = np.linspace(-5, 5, 50)
y = 2*X + np.random.normal(0, 1, size=50)

# Implement locally weighted regression
def locally_weighted_regression(test_point, X, y, tau):
    m = len(X)
    weights = np.exp(-(X - test_point)**2 / (2 * tau**2))
    theta = np.linalg.inv(X.T @ (weights * X)) @ (X.T @ (weights * y))
    prediction = test_point * theta
    return prediction

# Fit data points using locally weighted regression
predictions = []
tau = 1  # bandwidth parameter

for x in X:
    prediction = locally_weighted_regression(x, X, y, tau)
    predictions.append(prediction)

# Plot the graph
plt.scatter(X, y, label='Data')
plt.plot(X, predictions, color='red', label='Locally Weighted Regression')
plt.xlabel('X')
plt.ylabel('y')
plt.legend()
plt.show()
    """)
    
    
def pg3b():
    """
    3. Implement the non-parametric Locally Weighted Regressionalgorithm in order to fit data points.
    Select appropriate data set for your experiment and draw graphs
    """
    print(r"""
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import statsmodels.api as sm
x=[i/5.0 for i in range(30)]
y=[1,2,1,2,1,1,3,4,5,4,5,6,5,6,7,8,9,10,11,11,12,11,11,10,12,11,11,10,9,13]

lowess=sm.nonparametric.lowess(y,x)
lowess_x=list(zip(*lowess))[0]
lowess_y=list(zip(*lowess))[1]
f=interp1d(lowess_x,lowess_y,bounds_error=False)

xnew=[i/10.0 for i in range(100)]
ynew=f(xnew)
plt.plot(x,y,'o')
plt.plot(lowess_x,lowess_y,'+')
plt.plot(xnew,ynew,'-')
plt.show()
    """)

def pg4a():
    """
    4. Build an Artificial Neural Network by implementing the Backpropagation algorithm and test the same using appropriate data sets
    """
    print(r"""
import numpy as np

# Define the neural network class
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Initialize weights and biases
        self.W1 = np.random.randn(self.input_size, self.hidden_size)
        self.b1 = np.zeros((1, self.hidden_size))
        self.W2 = np.random.randn(self.hidden_size, self.output_size)
        self.b2 = np.zeros((1, self.output_size))

    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        return self.a2
    
    def backward(self, X, y, learning_rate):
        m = X.shape[0]
        
        grad_z2 = self.a2 - y
        grad_W2 = (1 / m) * np.dot(self.a1.T, grad_z2)
        grad_b2 = (1 / m) * np.sum(grad_z2, axis=0, keepdims=True)
        
        grad_a1 = np.dot(grad_z2, self.W2.T)
        grad_z1 = grad_a1 * (1 - np.power(self.a1, 2))
        grad_W1 = (1 / m) * np.dot(X.T, grad_z1)
        grad_b1 = (1 / m) * np.sum(grad_z1, axis=0, keepdims=True)
        
        self.W2 -= learning_rate * grad_W2
        self.b2 -= learning_rate * grad_b2
        self.W1 -= learning_rate * grad_W1
        self.b1 -= learning_rate * grad_b1
        
    def train(self, X, y, learning_rate, epochs):
        for epoch in range(epochs):
            output = self.forward(X)
            self.backward(X, y, learning_rate)
            loss = self.mean_squared_error(y, output)
            if epoch % 100 == 0:
                print(f"Epoch {epoch}: Loss = {loss}")
    
    def predict(self, X):
        return self.forward(X)
    
    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
    
    @staticmethod
    def mean_squared_error(y_true, y_pred):
        return np.mean(np.square(y_true - y_pred))

# Define the training data
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

# Create and train the neural network
nn = NeuralNetwork(input_size=2, hidden_size=4, output_size=1)
nn.train(X, y, learning_rate=0.1, epochs=1000)

# Test the neural network
predictions = nn.predict(X)
print("Predictions:", predictions)
    """)
    
def pg4b():
    """
    4. Build an Artificial Neural Network by implementing the Backpropagation algorithm and test the same using appropriate data sets.
    """
    print(r"""

import numpy as np
X = np.array(([2, 9], [1, 5], [3, 6]), dtype=float)
y = np.array(([92], [86], [89]), dtype=float)
X = X/np.amax(X,axis=0)
y = y/100
print(X)

def sigmoid (x):
    return 1/(1 + np.exp(-x))

def derivatives_sigmoid(x):
    return x * (1 - x)

epoch=5000 	
lr=0.1 		
inputlayer_neurons = 2 		
hiddenlayer_neurons = 3 	
output_neurons = 1

wh=np.random.uniform(size=(inputlayer_neurons,hiddenlayer_neurons))
bh=np.random.uniform(size=(1,hiddenlayer_neurons))
wout=np.random.uniform(size=(hiddenlayer_neurons,output_neurons))
bout=np.random.uniform(size=(1,output_neurons))

for i in range(epoch):
    hinp1=np.dot(X,wh)
    hinp=hinp1 + bh
    hlayer_act = sigmoid(hinp)
    outinp1=np.dot(hlayer_act,wout)
    outinp= outinp1+ bout
    output = sigmoid(outinp)
    n= 0
    EO = y-output
    outgrad = derivatives_sigmoid(output)
    d_output = EO* outgrad
    EH = d_output.dot(wout.T)
    hiddengrad = derivatives_sigmoid(hlayer_act)
    d_hiddenlayer = EH * hiddengrad

wout += hlayer_act.T.dot(d_output) *lr
wh += X.T.dot(d_hiddenlayer) *lr
n+=1
print("Input: \n" + str(X)) 
print("Actual Output: \n" + str(y))
print("Predicted Output: \n" ,output)
    """)

def pg4c():
    """
     4. Build an Artificial Neural Network by implementing the Backpropagation algorithm and test the same using appropriate data sets.
    """
    print(r"""
import numpy as np 

inputNeurons=2 
hiddenlayerNeurons=4 
outputNeurons=2 
iteration=6000

input = np.random.randint(1,5,inputNeurons) 
output = np.array([1.0,0.0]) 
hidden_layer=np.random.rand(1,hiddenlayerNeurons)

hidden_biass=np.random.rand(1,hiddenlayerNeurons) 
output_bias=np.random.rand(1,outputNeurons) 
hidden_weights=np.random.rand(inputNeurons,hiddenlayerNeurons) 
output_weights=np.random.rand(hiddenlayerNeurons,outputNeurons)

def sigmoid (layer):
    return 1/(1 + np.exp(-layer))

def gradient(layer): 
    return layer*(1-layer)

for i in range(iteration):

    hidden_layer=np.dot(input,hidden_weights) 
    hidden_layer=sigmoid(hidden_layer+hidden_biass)

    output_layer=np.dot(hidden_layer,output_weights) 
    output_layer=sigmoid(output_layer+output_bias)

    error = (output-output_layer) 
    gradient_outputLayer=gradient(output_layer)
    error_terms_output=gradient_outputLayer * error 
    error_terms_hidden=gradient(hidden_layer)*np.dot(error_terms_output,output_weights.T)

    gradient_hidden_weights = np.dot(input.reshape(inputNeurons,1),error_terms_hidden.reshape(1,hiddenlayerNeurons))
    gradient_ouput_weights = np.dot(hidden_layer.reshape(hiddenlayerNeurons,1),error_terms_output.reshape(1,outputNeurons))

    hidden_weights = hidden_weights + 0.05*gradient_hidden_weights 
    output_weights = output_weights + 0.05*gradient_ouput_weights 
    if i<50 or i>iteration-50:
        print("**********************") 
        print("iteration:",i,"::::",error) 
        print("###output########",output_layer)
    """)
   
def pg5a():
    """
    5. Demonstrate Genetic algorithm by taking a suitable data for any simple application.
    """
    print(r"""
import numpy as np

# Define the fitness function
def fitness_function(x):
    return x**2

# Define the genetic algorithm
def genetic_algorithm(population_size, num_generations):
    population = np.random.randint(low=-10, high=10, size=population_size)
    
    for generation in range(num_generations):
        fitness = np.array([fitness_function(x) for x in population])
        parents = np.random.choice(population, size=population_size, p=fitness/np.sum(fitness))
        offspring = []
        
        for i in range(0, population_size, 2):
            parent1 = parents[i]
            parent2 = parents[i+1]
            crossover_point = np.random.randint(1, high=32)
            child1 = (parent1 & (2**crossover_point-1)) + (parent2 & (2**(32-crossover_point)-1))
            child2 = (parent2 & (2**crossover_point-1)) + (parent1 & (2**(32-crossover_point)-1))
            offspring.append(child1)
            offspring.append(child2)
        
        population = np.array(offspring)
    
    return population

# Run the genetic algorithm
population_size = 10
num_generations = 10
final_population = genetic_algorithm(population_size, num_generations)
print("Final Population:", final_population)


    """)
    
def pg6a():
    """
    6. Demonstrate Q learning algorithm with suitable assumption for a problem statement.
    """
    print(r"""

import numpy as np

# Define the Q-learning algorithm
def q_learning(num_episodes, alpha, gamma, epsilon):
    # Define the environment
    rewards = np.array([[0, -1, 0, -1],
                       [0, 0, -1, -1],
                       [0, -1, 0, 100],
                       [-1, -1, -1, 0]])
    
    num_states = rewards.shape[0]
    num_actions = rewards.shape[1]
    Q = np.zeros((num_states, num_actions))
    
    for episode in range(num_episodes):
        state = np.random.randint(num_states)
        done = False
        
        while not done:
            if np.random.rand() <= epsilon:
                action = np.random.randint(num_actions)
            else:
                action = np.argmax(Q[state, :])
            
            next_state = action
            reward = rewards[state, action]
            
            Q[state, action] = (1 - alpha) * Q[state, action] + alpha * (reward + gamma * np.max(Q[next_state, :]))
            
            state = next_state
            
            if state == num_states - 1:
                done = True
    
    return Q

# Run the Q-learning algorithm
num_episodes = 1000
alpha = 0.1
gamma = 0.9
epsilon = 0.1
Q_values = q_learning(num_episodes, alpha, gamma, epsilon)
print("Q-values:", Q_values)
    """)
