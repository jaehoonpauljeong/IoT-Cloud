#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#define SIZE 10
#define PI 3.141593
#define EXP 2.718282
#define BOUND 100

using namespace std;

class Position{
	private:
		double x;
		double y;
	public:
		Position(double _x = 0, double _y = 0) : x(_x), y(_y)
		{}
		double getX() const{
			return x;
		}
		double getY() const{
			return y;
		}
		void setX(double _x){
			this->x = _x;
		}
		void setY(double _y){
			this->y = _y;
		}
};

class Distance : public Position{
	private:
		double dist;
	public:
		Distance(double _x = 0 , double _y =0, double _dist = 0) : Position(_x, _y), dist(_dist)
		{}
		double getDist() const{
			return dist;
		}
		void setDist(double _dist){
			this->dist = _dist;
		}
};

class Info : public Position{
    private:
        long long int timestamp;
        int rssi;
    public:
		Info(double _x =0, double _y =0,long long int _t =0, int _r=0)
		 : Position(_x,_y), timestamp(_t), rssi(_r)
		{}
        long long int getTimestamp() const{
			return timestamp;
        }
		void setTimeStamp(long long int _timestamp){
			this->timestamp = _timestamp;
		}

		int getRssi() const{
			return rssi;
		}
		void setRssi(int _rssi){
			this->rssi = _rssi;
		}
		Position getPos(){
			Position pos(this->getX(), this->getY());
			return pos;
		}
};

class Table : public Position{
	private:
		int power;
		double distance;
		double avg_dist;
		double std_dev;
	public:
		Table(double _x =0, double _y = 0, int _p =0, double _d =0, double _s = 0)
			: Position(_x,_y), power(_x), distance(_d), avg_dist(_d), std_dev(_s)
		{}
		int getPower() const{
			return power;
		}
		void setPower(int _power){
			this->power = _power;
		}
		double getDistance() const{
			return distance;
		}
		double getAvg_dist() const{
			return avg_dist;
		}
		double getStd_dev() const{
			return std_dev;
		}
		void setDistance(double _distance){
			this->distance = _distance;
		}
		void setAvg_dist(double _avg_dist){
			this->avg_dist = _avg_dist;
		}
		void setStd_dev(double _std_dev){
			this->std_dev = _std_dev;
		}
};

class Wall{
	private:
		int wallEnd;
		int wallStart;
		int startBound;
		int endBound;
	public:
		Wall() : wallEnd(2000), wallStart(0), startBound(100), endBound(1900)
		{}
		int getEnd(){
			return wallEnd;
		} 
		int getStart(){
			return wallStart;
		}
		int getSB(){
			return startBound;
		}
		int getEB(){
			return endBound;
		}
};

bool desc(Info a, Info b);
bool incr(Distance a, Distance b);
double gaussDistrubution(const double mean, const double theta, const double x);
double getDistance(const Position pos1, const Position pos2);
double getDistanceXY(const double x1, const double y1, const double x2, const double y2);
Position rssiCentroidEstimation(vector<Info> &data);
void getAvgDist_StdDev(vector<Table>& powerDistTab, vector<Info> &data, const Position pos);
vector<Table> powerDistanceTableConstruct(vector<Info> &data, const Position pos);
Position gridWeightMap(vector<Table> &powerTable);
static PyObject *csala_sala_algorithms(PyObject *self, PyObject *args);

bool desc(Info a, Info b){
	return a.getRssi() > b.getRssi();
}

bool incr(Distance a, Distance b){
	return a.getDist() < b.getDist();
}

double gaussDistrubution(const double mean, const double theta, const double x){
	double result;
	double front = 1/(theta * sqrt(2*PI));
	double exponentUp = -pow((x-mean),2);
	double exponentDown = 2*pow(theta, 2);
	double exponent = exponentUp / exponentDown;
	result = front * pow(EXP, exponent);
	return result;
}

double getDistance(const Position pos1, const Position pos2){
	double distance;

	double sub_x = pos1.getX() - pos2.getX();
	double sub_y = pos1.getY() - pos2.getY();
	distance = sqrt(pow(sub_x, 2) + pow(sub_y,2));
	return distance;
}

double getDistanceXY(const double x1, const double y1, const double x2, const double y2){
	double sub_x = x1 - x2;
	double sub_y = y1 - y2;
	
	return sqrt(pow(sub_x,2) + pow(sub_y,2));
}

Position rssiCentroidEstimation(vector<Info> &data){
	double sum_x = 0;
	double sum_y = 0;
	Position pos;

	sort(data.begin(), data.end(), desc);
	for(int i=0; i<SIZE; i++){
		sum_x += data.at(i).getX();
		sum_y += data.at(i).getY();
	}

	pos.setX(sum_x / SIZE);
	pos.setY(sum_y / SIZE);

	return pos;
}

int isRangeX(int x){
	Wall wall;
	if(x < wall.getSB())
		return 0;
	else if(x > wall.getEB())
		return 2;
	else
		return 1;	
}

int isRangeY(int y){
	Wall wall;
	if(y > wall.getEB())
		return 0;
	else if(y < wall.getSB())
		return 2;
	else
		return 1;	
}

int checkWallCorner(const Position& pos){
	int check = -1;
	int checkX = isRangeX(pos.getX());
	int checkY = isRangeY(pos.getY());
	if(checkX == 1 && checkY == 1){
		check = 0;
	}
	else if(checkX == 1 && checkY == 0){
		check = 1;
	}
	else if(checkX == 2 && checkY == 0){
		check = 2;
	}
	else if(checkX == 2 && checkY == 1){
		check = 3;
	}
	else if(checkX == 2 && checkY == 2){
		check = 4;
	}
	else if(checkX == 1 && checkY == 2){
		check = 5;
	}
	else if(checkX == 0 && checkY == 2){
		check = 6;
	}
	else if(checkX == 0 && checkY == 1){
		check = 7;
	}
	else{ // checkX == 0 && checkY == 0
		check = 8;
	}
	return check;
}

void wallCornerHandling(Position& pos, vector<Info>& data){
/* 
	다음과 같이 위치에 Centroid 위치에 따라 다른 값을 갖게 된다.
	|	8	|		1		|	2	|
	---------------------------------
	|		|				|		|
	|	7	|		0		|	3	|
	|		|				|		|
	---------------------------------
	|	6	|		5		|	4	|
	
*/
	Wall wall;
	vector<Info> temp;
	for(int i=0; i<SIZE; i++){
		temp.push_back(data.at(i));
	}
	// 여기에 정렬된 10개의 Sample Point 가 있다.

	int check = checkWallCorner(pos);
	switch(check){		// 대충 이런식으로 짜면 됨.
		case 0:	// 벽이나 코너에 없다.
			return;
		case 1:	// 1번 벽 처리
			pos.setY(wall.getEnd());
			break;
		case 5: // 5번 벽 처리
			pos.setY(wall.getStart());
			break;
		case 3:	// 3번 벽 처리
			pos.setX(wall.getEnd());
			break;
		case 7: // 7번 벽 처리
			pos.setX(wall.getStart());
			break;
		case 2:	// 2번 코너 처리
			pos.setX(wall.getEnd());
			pos.setY(wall.getStart());
			break;
		case 4: // 4번 코너 처리
			pos.setX(wall.getEnd());
			pos.setY(wall.getStart());
			break;
		case 6: // 6번 코너 처리
			pos.setX(wall.getStart());
			pos.setY(wall.getStart());
			break;
		case 8: // 8번 코너 처리
			pos.setX(wall.getStart());
			pos.setY(wall.getEnd());
			break;
	;}
}

void getAvgDist_StdDev(vector<Table>& powerDistTab, vector<Info> &data, const Position pos){
	vector<Distance> dist;
	vector<double> dist2;
	
	for(int i=0; i<SIZE; i++){
		
		double x = powerDistTab.at(i).getX();
		double y = powerDistTab.at(i).getY();
		dist.clear();
		for(int j=0; j<(int)data.size(); j++){
			double tempdist;
			tempdist = getDistanceXY(x, y, data.at(j).getX(), data.at(j).getY());
			dist.push_back(Distance(data.at(j).getX(), data.at(j).getY(), tempdist));
		}
		sort(dist.begin(), dist.end(), incr);
		double sum = 0;
		for(int k=0; k<SIZE; k++){
			double temp = getDistanceXY(dist.at(k).getX(), dist.at(k).getY(), pos.getX(), pos.getY());
			dist2.push_back(temp);
			sum += temp;
		}
		sum = sum / 10;
		powerDistTab.at(i).setAvg_dist(sum);
		//// 여기까지 Average Distance 구하기!


		//// 여기부터 Std Deviation 구하기!
		double tempsum = 0;
		for(int l=0; l<SIZE; l++){
			double sub = dist2.at(l) - sum;
			double square = pow(sub,2);
			tempsum += square;
		}
		dist2.clear();
		tempsum = tempsum / 10;
		double result = sqrt(tempsum);
		powerDistTab.at(i).setStd_dev(result);
	}
}

vector<Table> powerDistanceTableConstruct(vector<Info> &data, const Position pos){
	vector<Table> powerDistTab;
	Table tempTable;
	Position posTemp;
	double distance = 0;

	for(int i=0; i<SIZE; i++){
		tempTable.setX(data.at(i).getX());
		tempTable.setY(data.at(i).getY());
		tempTable.setPower(data.at(i).getRssi());
		distance = getDistance(data.at(i).getPos(), pos);
		tempTable.setDistance(distance);
		powerDistTab.push_back(tempTable);
	}

	getAvgDist_StdDev(powerDistTab, data, pos);
	return powerDistTab;
}

Position gridWeightMap(vector<Table> &powerTable){
	double distance, maxPosibility = 0;
	int max_X=0, max_Y=0;
	const int gridMapSize = 1000;
	const int gridSize = 10;
	const int gridNum = gridMapSize / gridSize;

	Position **gridArr = new Position*[gridNum];
	for(int i=0; i<gridNum; i++){
		gridArr[i] = new Position[gridNum];
	}

	for(int i=0; i<gridNum; i++){
		for(int j=0; j<gridNum; j++){
			gridArr[i][j] = Position(10*j+5, 10*i+5);
		}
	}

	double **posibilityArr = new double*[gridNum];
	for(int i=0; i<gridNum; i++){
		posibilityArr[i] = new double[gridNum];
	}

	for(int i=0; i<gridNum; i++){
		for(int j=0; j<gridNum; j++){
			posibilityArr[i][j] = 0;
		}
	}

	for(int i=0; i<SIZE; i++){
		for(int j=0; j<gridNum; j++){
			for(int k=0; k<gridNum; k++){
				distance = getDistanceXY(gridArr[j][k].getX(), gridArr[j][k].getY(), powerTable.at(i).getX(), powerTable.at(i).getY());
				posibilityArr[j][k] += gaussDistrubution(powerTable.at(i).getAvg_dist(), powerTable.at(i).getStd_dev(), distance);
				
				if(maxPosibility < posibilityArr[j][k]){
					maxPosibility = posibilityArr[j][k];
					max_X = j;
					max_Y = k;
				}
			}
		}
	}

	double X = gridArr[max_X][max_Y].getX();
	double Y = gridArr[max_X][max_Y].getY();
	//delete all arrays
	for(int i=0; i<gridNum; i++){
		delete[] gridArr[i];
	}
	delete[] gridArr;

	for(int i=0; i<gridNum; i++){
		delete[] posibilityArr[i];
	}
	delete[] posibilityArr;
	return Position(X,Y);
}


static PyObject *csala_sala_algorithms(PyObject *self, PyObject *args) {

    PyObject *device, *reports;
    double pos_star_x, pos_star_y;
    double location_x, location_y;
	vector<Info> data;
	vector<Table> powerTable;
	Info rssiCE;
	Position pos;

	if (!PyArg_ParseTuple(args, "OO", &device, &reports)) {
		return Py_BuildValue("i", -1);
	}

	//PyObject_Print(device, stderr, 0);
	fprintf(stderr, "c++: starting...\n");

	int report_size = PySequence_Size(reports);


	for ( int ri=0; ri<report_size; ri++ ) {

		PyObject *report_recode;
		report_recode = PySequence_GetItem(reports, ri);

		PyObject *py_position, *py_rssi, *py_timestamp;

		py_position = PyObject_GetAttrString(report_recode, "position");
		py_rssi =  PyObject_GetAttrString(report_recode, "rssi");
		py_timestamp =  PyObject_GetAttrString(report_recode, "timestamp");

		rssiCE.setX(PyLong_AsLong( PyObject_GetAttrString(py_position, "x") ));
		rssiCE.setY(PyLong_AsLong( PyObject_GetAttrString(py_position, "y") ));
		rssiCE.setTimeStamp(PyLong_AsLongLong(py_timestamp));
		rssiCE.setRssi(PyLong_AsLong(py_rssi));
		data.push_back(rssiCE);
	}

	fprintf(stderr, "c++: done init\n");

	pos = rssiCentroidEstimation(data);
	fprintf(stderr, "c++: done rssi\n");

	wallCornerHandling(pos, data);
	fprintf(stderr, "c++: done wc handling\n");

	powerTable = powerDistanceTableConstruct(data, pos);
	fprintf(stderr, "c++: done pdt construct\n");

	Position finalPos = gridWeightMap(powerTable);
	fprintf(stderr, "c++: done gwm\n");

	pos_star_x = pos.getX();
	pos_star_y = pos.getY();
	location_x = finalPos.getX();
	location_y = finalPos.getY();


	fprintf(stderr, "c++: gonna return %lf %lf %lf %lf\n", pos_star_x, pos_star_y, location_x, location_y);
	//return Py_BuildValue("ffff", 0.0, 0.0, 0.0, 0.0);
	return Py_BuildValue("ffff", pos_star_x, pos_star_y, location_x, location_y);
}


static PyMethodDef csalaMethods[] = {

     {"sala_algorithms", csala_sala_algorithms, METH_VARARGS,
     "c-SALA wrapper"},

    {NULL, NULL, 0, NULL} /* Sentinel */
};

// METH_VARARGS, METH_NOARGS 에 대한 설명
/*
Note the third entry (METH_VARARGS). This is a flag telling the interpreter the calling convention to be used for the C function. It should normally always be METH_VARARGS or METH_VARARGS | METH_KEYWORDS; a value of 0 means that an obsolete variant of PyArg_ParseTuple() is used.

When using only METH_VARARGS, the function should expect the Python-level parameters to be passed in as a tuple acceptable for parsing via PyArg_ParseTuple(); more information on this function is provided below.

The METH_KEYWORDS bit may be set in the third field if keyword arguments should be passed to the function. In this case, the C function should accept a third PyObject * parameter which will be a dictionary of keywords. Use PyArg_ParseTupleAndKeywords() to parse the arguments to such a function.
*/


// 모듈의 문서 상수. 이 모듈이 어떤 모듈인지 텍스트를 통해 설명할 때 사용
// NULL 이어도 문제없음
static char csala_doc[] = "moudle documentation\n";

// 파이썬 모듈 정의부
static struct PyModuleDef csalamodule = {

	PyModuleDef_HEAD_INIT,
	"csala",	/* name of module */
	csala_doc,	/* module documentation, may be NULL */
	-1,			/* size of per-interpreter state of the module,
				   or -1 if the module keeps state in global variables. */
	csalaMethods	/* 모듈 내의 함수 정의부 */
};


PyMODINIT_FUNC PyInit_csala(void) {

	return PyModule_Create(&csalamodule);
}
