cmake_minimum_required(VERSION 3.16.3)

project(Lecture_4_Pose_Estimation)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(CTest)

find_package(OpenCV REQUIRED)
find_package(fmt REQUIRED)

function(configure_lecture4_target target_name)
    target_include_directories(${target_name} PRIVATE ${PROJECT_SOURCE_DIR})
    target_link_libraries(${target_name} PRIVATE ${OpenCV_LIBS} fmt::fmt)

    foreach(asset IN ITEMS video.avi tiny_resnet.onnx)
        add_custom_command(
            TARGET ${target_name}
            POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                ${PROJECT_SOURCE_DIR}/${asset}
                $<TARGET_FILE_DIR:${target_name}>/${asset}
        )
    endforeach()
endfunction()

# 学生填写版：只需修改 src/main.cpp 与 tasks/pose_solver.cpp 的 Task 标记区域。
add_executable(lecture4_class
    src/main.cpp
    tasks/detector.cpp
    tasks/pose_solver.cpp
)
configure_lecture4_target(lecture4_class)

# 教师参考答案：与学生版共享检测器和运行资源，方便逐文件对照。
add_executable(lecture4_answer
    ${PROJECT_SOURCE_DIR}/../answer/main.cpp
    tasks/detector.cpp
    ${PROJECT_SOURCE_DIR}/../answer/pose_solver.cpp
)
configure_lecture4_target(lecture4_answer)

if(BUILD_TESTING)
    # 学生完成后运行的验收测试。
    add_executable(lecture4_pose_test
        tests/pose_solver_test.cpp
        tasks/pose_solver.cpp
    )
    target_include_directories(lecture4_pose_test PRIVATE ${PROJECT_SOURCE_DIR})
    target_link_libraries(lecture4_pose_test PRIVATE ${OpenCV_LIBS})
    add_test(NAME lecture4_pose_test COMMAND lecture4_pose_test)

    # 教师在课前可直接验证参考答案，不依赖学生填写版。
    add_executable(lecture4_answer_test
        tests/pose_solver_test.cpp
        ${PROJECT_SOURCE_DIR}/../answer/pose_solver.cpp
    )
    target_include_directories(lecture4_answer_test PRIVATE ${PROJECT_SOURCE_DIR})
    target_link_libraries(lecture4_answer_test PRIVATE ${OpenCV_LIBS})
    add_test(NAME lecture4_answer_test COMMAND lecture4_answer_test)
endif()
