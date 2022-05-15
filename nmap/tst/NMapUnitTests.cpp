/**
# ##############################################################################
#  Copyright (c) 2021- University of Bonn                            		   #
#  All rights reserved.                                                        #
#                                                                              #
#  Author: Nicky Zimmerman                                     				   #
#                                                                              #
#  File: MSensorsUnitTests.cpp                                                            #
# ##############################################################################
**/

#include "gtest/gtest.h"
#include <opencv2/opencv.hpp>
#include <iostream>
#include <math.h>
#include <string>
#include <fstream>
#include <chrono>
#include <stdlib.h>
#include <string>

#include "GMap.h"
#include "Object.h"
#include <fstream>
#include "Room.h"
#include "FloorMap.h"
#include <nlohmann/json.hpp>



TEST(TestObject, test1) {
    
    std::string jsonPath = std::string(PROJECT_TEST_DATA_DIR) + "object.config";
   // Object obj(jsonPath);

    using json = nlohmann::json;
    std::ifstream file(jsonPath);
    json config;
    file >> config;

    Object obj(config);

    Eigen::Vector4f pos = obj.Position();

    ASSERT_EQ(obj.SemLabel(), 0);
    ASSERT_EQ(pos(0), 1);
    ASSERT_EQ(pos(1), 5);

}

TEST(TestRoom, test1) {
    
    std::string jsonPath = std::string(PROJECT_TEST_DATA_DIR) + "room.config";

    using json = nlohmann::json;
    std::ifstream file(jsonPath);
    json config;
    file >> config;

    Room room(config);


    ASSERT_EQ(room.Name(), "Room 1");
    ASSERT_EQ(room.ID(), 5);

    std::vector<Object> objects = room.Objects();
    ASSERT_EQ(objects[1].SemLabel(), 1);

}



TEST(TestFloorMap, test1) {
    
    std::string jsonPath = std::string(PROJECT_TEST_DATA_DIR) + "floor.config";

    using json = nlohmann::json;
    std::ifstream file(jsonPath);
    json config;
    file >> config;

    FloorMap floor(config, std::string(PROJECT_TEST_DATA_DIR));

    std::vector<std::string> classes = floor.Classes();
    std::vector<Room> rooms =  floor.GetRooms();


    ASSERT_EQ(classes[0], "sink");
    ASSERT_EQ(rooms[0].Name(), "Room 1");

    std::vector<Object> objects = rooms[1].Objects();
    ASSERT_EQ(objects[1].SemLabel(), 4);

}





int main(int argc, char **argv) {
   ::testing::InitGoogleTest(&argc, argv);
   return RUN_ALL_TESTS();
}



