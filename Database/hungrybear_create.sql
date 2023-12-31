-- hungrybear 초기화 후 데이터베이스 생성

IF EXISTS(SELECT name FROM sys.databases WHERE (name = 'Hungrybear') OR (name = 'hungrybear'))
     DROP DATABASE [Hungrybear];
CREATE DATABASE Hungrybear

--테이블 생성 (food, dailycal, customer)

USE [hungrybear]

--음식 테이블
CREATE TABLE food (
  foodID	INT PRIMARY KEY,
  foodname    VARCHAR(20),
  foodcal int,
);
-- 고객 테이블
CREATE TABLE customer (
  customerID INT PRIMARY KEY,
  name VARCHAR(20),
  weight int,
  high int,
  age int,
  gender VARCHAR(20),
);

--음식 칼로리를 가져오기위한 테이블
CREATE TABLE dailycal (
  dailycalID INT PRIMARY KEY,
  foodID INT REFERENCES food(foodID),
  customerID INT REFERENCES customer(customerID),
  eat_food INT NULL
);

INSERT INTO food VALUES (1, 'beef_tartare', 400);
INSERT INTO food VALUES (2, 'chicken_curry', 500);
INSERT INTO food VALUES (3, 'chocolate_mousse', 400);
INSERT INTO food VALUES (4, 'french_toast', 400);
INSERT INTO food VALUES (5, 'fried_rice', 400);
INSERT INTO food VALUES (6, 'hot_dog', 300);
INSERT INTO food VALUES (7, 'ice_cream', 300);
INSERT INTO food VALUES (8, 'lasagna', 200);
INSERT INTO food VALUES (9, 'oysters', 200);
INSERT INTO food VALUES (10, 'pizza', 500);
INSERT INTO food VALUES (11, 'takoyaki', 400);
