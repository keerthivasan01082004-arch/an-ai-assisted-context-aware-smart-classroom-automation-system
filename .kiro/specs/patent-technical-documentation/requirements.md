# Requirements Document: Smart Classroom AI System - Patent Technical Documentation

## Introduction

This document specifies the requirements for creating comprehensive patent documentation for a Smart Classroom AI System. The system integrates computer vision, optical character recognition, environmental monitoring, predictive analytics, and automated device control to optimize classroom operations. The patent documentation must provide detailed technical specifications suitable for patent office filing, covering five key technical areas with complete algorithmic details, formulas, implementation methods, and technical specifications.

## Glossary

- **Documentation_System**: The system responsible for extracting, organizing, and documenting technical specifications from the existing Smart Classroom AI implementation
- **AI_Detection_Module**: YOLOv8-based person detection and dlib-based face recognition system for student identification and counting
- **OCR_Engine**: Optical Character Recognition system for timetable parsing with preprocessing, extraction, and validation
- **Comfort_Calculator**: Environmental monitoring system that calculates comfort scores based on temperature, humidity, noise, CO2, and occupancy
- **Prediction_Engine**: Machine learning system for forecasting occupancy, energy consumption, and optimal environmental conditions
- **Device_Controller**: Automated control system for lights, fans, and air conditioning based on environmental conditions and occupancy
- **Patent_Document**: Comprehensive technical specification document suitable for patent office submission
- **Technical_Specification**: Detailed description including algorithms, formulas, parameters, thresholds, and implementation details
- **YOLOv8n**: You Only Look Once version 8 nano model for real-time object detection
- **dlib**: C++ library with Python bindings for face recognition using deep learning
- **Tesseract_OCR**: Open-source optical character recognition engine
- **EARS_Pattern**: Easy Approach to Requirements Syntax - structured requirement format
- **Environmental_Sensor**: IoT device measuring temperature, humidity, noise, CO2, or light levels
- **Comfort_Score**: Numerical value (0-100) representing environmental comfort based on multiple parameters
- **Energy_Prediction**: Forecasted power consumption in kilowatt-hours (kWh) based on device states and occupancy

## Requirements

### Requirement 1: AI Student Detection Technical Specification

**User Story:** As a patent examiner, I want detailed technical specifications for the AI student detection system, so that I can understand the novel aspects of the person counting and identification method.

#### Acceptance Criteria

1. THE Documentation_System SHALL extract and document the complete YOLOv8n model architecture including model type, version, input dimensions, and detection parameters
2. WHEN documenting the detection method, THE Documentation_System SHALL specify the person counting algorithm including confidence thresholds, bounding box processing, and duplicate elimination logic
3. THE Documentation_System SHALL document the edge processing architecture including frame skip intervals, buffer sizes, FPS settings, and latency optimization techniques
4. THE Documentation_System SHALL specify the face recognition integration including dlib model architecture, encoding generation method, face comparison algorithm, and matching tolerance values
5. THE Documentation_System SHALL document the camera preprocessing pipeline including rotation transformations, zoom calculations, pan offset computations, and frame cropping algorithms
6. WHEN multiple detection methods exist, THE Documentation_System SHALL document the fallback logic from face recognition to generic person detection
7. THE Documentation_System SHALL specify all numerical parameters including confidence thresholds (e.g., 0.6 tolerance), frame processing intervals (every 3rd frame), and JPEG compression quality (60%)

### Requirement 2: Timetable OCR Logic Technical Specification

**User Story:** As a patent examiner, I want comprehensive documentation of the OCR extraction pipeline, so that I can evaluate the novelty of the multi-strategy preprocessing and intelligent parsing approach.

#### Acceptance Criteria

1. THE Documentation_System SHALL document all five preprocessing methods including Adaptive Threshold, OTSU Threshold, Denoising, CLAHE Enhancement, and Morphological Operations with complete parameter specifications
2. WHEN documenting preprocessing, THE Documentation_System SHALL specify kernel sizes (5x5 Gaussian, 2x2 morphological), threshold parameters (block size 11, constant 2), and CLAHE parameters (clipLimit 2.0, tileGridSize 8x8)
3. THE Documentation_System SHALL document the red color detection algorithm including HSV color ranges (lower_red1: [0,70,50] to upper_red1: [10,255,255], lower_red2: [170,70,50] to upper_red2: [180,255,255]) and contour area thresholds (>500 pixels)
4. THE Documentation_System SHALL specify the multi-strategy OCR extraction including PSM modes (6, 4, 3), text combination logic, and best-result selection criteria
5. THE Documentation_System SHALL document the table structure detection algorithm including edge detection parameters (Canny 50-150), morphological kernels (40x1 horizontal, 1x40 vertical), and cell filtering thresholds (width >50, height >20)
6. THE Documentation_System SHALL specify the intelligent parsing regex pattern for timetable entries: ([A-Z]+\d+)-([A-Z]{3}\d{4}[A-Z]?)-([A-Z]{2,4})-([A-Z]{2,4}\d{2,4})-ALL
7. THE Documentation_System SHALL document the course code validation algorithm including fuzzy matching with cutoff threshold (0.75), pattern validation regex, and correction logic
8. THE Documentation_System SHALL specify the error handling mechanisms for OCR failures, invalid course codes, and missing day markers with fallback distribution strategies

### Requirement 3: Comfort Score Calculation Method

**User Story:** As a patent examiner, I want the complete comfort score formula with all parameters and weightings, so that I can understand the environmental optimization algorithm.

#### Acceptance Criteria

1. THE Documentation_System SHALL document the comfort score formula starting from base value 100 with all deduction calculations
2. THE Documentation_System SHALL specify temperature impact calculations: deduction = (18 - temperature) * 5 for temperatures below 18°C, and deduction = (temperature - 26) * 4 for temperatures above 26°C
3. THE Documentation_System SHALL specify noise impact calculation: deduction = (noise - 40) * 1.5 for noise levels above 40 dB
4. THE Documentation_System SHALL specify CO2 impact calculation: deduction = (co2 - 800) * 0.02 for CO2 levels above 800 ppm
5. THE Documentation_System SHALL specify humidity impact calculations: deduction = (40 - humidity) * 0.5 for humidity below 40%, and deduction = (humidity - 60) * 0.8 for humidity above 60%
6. THE Documentation_System SHALL specify overcrowding impact calculation: deduction = (people_count - 40) * 2 for occupancy above 40 people
7. THE Documentation_System SHALL document the comfort score range constraint ensuring final values remain between 0 and 100 using max(0, min(100, comfort))
8. THE Documentation_System SHALL specify optimal environmental ranges: temperature 22-26°C, noise <40 dB, CO2 <800 ppm, humidity 40-60%, occupancy <40 people

### Requirement 4: Prediction Model Technical Specification

**User Story:** As a patent examiner, I want detailed specifications of all prediction algorithms, so that I can evaluate the forecasting methodology and accuracy approach.

#### Acceptance Criteria

1. THE Documentation_System SHALL document the energy consumption prediction formula including base load (0.5 kWh), lighting calculation (0.3 * people_count/50), fan power levels (OFF: 0, LOW: 0.075, MEDIUM: 0.15, HIGH: 0.25 kWh), and AC consumption (2.5 + (temperature - 22) * 0.1 kWh)
2. THE Documentation_System SHALL specify the optimal temperature prediction algorithm: optimal = 24 - (people_count / 100), and time_to_optimal = temperature_difference * 2 minutes per degree
3. THE Documentation_System SHALL document the next hour occupancy prediction logic based on time patterns: peak hours (10-12, 14-16) predict 35-45 people, regular class hours (8-18) predict 20-35 people, non-class hours predict 0-5 people
4. THE Documentation_System SHALL specify the productivity score calculation combining comfort (40% weight), noise impact (0-30 points based on <40, <55, <70, >70 dB thresholds), CO2 impact (5-20 points based on <600, <800, <1000, >1000 ppm), and temperature impact (0-10 points based on 20-24°C optimal range)
5. THE Documentation_System SHALL document the class end time prediction algorithm using standard 50-minute class durations and common end times (08:50, 09:50, 10:50, 11:50, 12:50, 14:50, 15:50, 16:50, 17:50)
6. THE Documentation_System SHALL specify the next class prediction logic including same-day search, next-day rollover with 7-day lookahead, and minutes-until calculation
7. THE Documentation_System SHALL document the occupancy trend calculation using 3-sample moving window with threshold of ±5 people for trend detection (Increasing, Decreasing, Stable)
8. THE Documentation_System SHALL specify the carbon footprint calculation: CO2_kg = energy_kWh * 0.82, and trees_equivalent = CO2_kg / (21/365) for daily offset

### Requirement 5: Device Control Logic Technical Specification

**User Story:** As a patent examiner, I want complete specifications of the automated device control rules and decision logic, so that I can understand the intelligent automation system.

#### Acceptance Criteria

1. THE Documentation_System SHALL document the zero-occupancy rule: WHEN people_count equals 0, THE Device_Controller SHALL set lights to OFF, fan to OFF, AC to OFF, and mode to "Idle - Energy Saving"
2. THE Documentation_System SHALL specify the temperature-based control rules with five distinct zones: <24°C (fan OFF, AC OFF), 24-27°C (fan LOW, AC OFF), 27-29°C (fan MEDIUM, AC OFF), 29-31°C (fan HIGH, AC ON at 24°C), ≥31°C (fan HIGH, AC ON at 22°C)
3. THE Documentation_System SHALL document the lighting control rule: WHEN people_count is greater than 0, THE Device_Controller SHALL set lights to ON
4. THE Documentation_System SHALL specify the mode classification logic mapping environmental conditions to operational modes: "Optimal Comfort" (<24°C), "Comfortable" (24-27°C), "Moderate Cooling" (27-29°C), "High Cooling" (29-31°C), "Maximum Cooling" (≥31°C)
5. THE Documentation_System SHALL document the noise-based mode override: WHEN noise exceeds 70 dB, THE Device_Controller SHALL set mode to "High Noise Alert", WHEN noise exceeds 55 dB, THE Device_Controller SHALL set mode to "Moderate Noise"
6. THE Documentation_System SHALL specify the overcrowding alert rule: WHEN people_count exceeds 40, THE Device_Controller SHALL set mode to "Overcrowded" and trigger ventilation recommendations
7. THE Documentation_System SHALL document the energy calculation integration: FOR ALL device state changes, THE Device_Controller SHALL invoke predict_energy_consumption with current people_count, temperature, and device actions
8. THE Documentation_System SHALL specify the anomaly detection rules including after-hours activity (people_count >0 when hour <7 or >20), extreme temperature (>35°C fire risk, <15°C HVAC failure), excessive noise (>85 dB emergency), dangerous CO2 (>1500 ppm), and overcrowding safety (>50 people fire limit)

### Requirement 6: Documentation Structure and Format

**User Story:** As a patent attorney, I want the documentation organized in a clear, patent-office-ready format, so that I can efficiently prepare the patent application.

#### Acceptance Criteria

1. THE Documentation_System SHALL create a Patent_Document with five main sections corresponding to the five technical areas
2. WHEN organizing content, THE Documentation_System SHALL include subsections for: Algorithm Description, Mathematical Formulas, Parameters and Thresholds, Implementation Details, and Novel Aspects
3. THE Documentation_System SHALL format all mathematical formulas using clear notation with variable definitions
4. THE Documentation_System SHALL include all numerical constants, thresholds, and configuration values extracted from the implementation
5. THE Documentation_System SHALL document data flow diagrams showing input sources, processing steps, and output destinations for each technical area
6. THE Documentation_System SHALL specify hardware requirements including camera specifications, sensor types, and processing requirements
7. THE Documentation_System SHALL include code references mapping each specification to the source implementation file and function name

### Requirement 7: Technical Accuracy and Completeness

**User Story:** As a patent examiner, I want the documentation to be technically accurate and complete, so that I can properly evaluate the patent application.

#### Acceptance Criteria

1. THE Documentation_System SHALL extract all specifications directly from the actual implementation code without assumptions or generalizations
2. WHEN documenting algorithms, THE Documentation_System SHALL include all conditional branches, edge cases, and error handling logic
3. THE Documentation_System SHALL verify that all numerical values match the implementation exactly
4. THE Documentation_System SHALL document all dependencies including library versions (YOLOv8, dlib, Tesseract, OpenCV, face_recognition)
5. THE Documentation_System SHALL specify data types, ranges, and units for all parameters (e.g., temperature in °C, noise in dB, CO2 in ppm, energy in kWh)
6. THE Documentation_System SHALL include timing specifications (frame intervals, prediction intervals, update frequencies)
7. THE Documentation_System SHALL document all integration points between modules including state management and data flow

### Requirement 8: Novel Aspects Identification

**User Story:** As a patent attorney, I want clear identification of novel and non-obvious aspects, so that I can emphasize them in the patent claims.

#### Acceptance Criteria

1. THE Documentation_System SHALL identify the multi-strategy OCR preprocessing approach combining five different methods as a novel aspect
2. THE Documentation_System SHALL highlight the red color detection for visual context understanding in timetable parsing as a novel feature
3. THE Documentation_System SHALL identify the multi-factor comfort score calculation with weighted environmental parameters as a novel algorithm
4. THE Documentation_System SHALL highlight the predictive temperature optimization based on occupancy forecasting as a novel approach
5. THE Documentation_System SHALL identify the integrated anomaly detection combining temporal, environmental, and safety rules as a novel system
6. THE Documentation_System SHALL highlight the hybrid detection approach combining YOLOv8 person detection with dlib face recognition as a novel architecture
7. THE Documentation_System SHALL identify the intelligent timetable parsing with fuzzy course code validation and day-based distribution as a novel method
8. THE Documentation_System SHALL document the energy-aware device control with predictive optimization as a novel automation approach

## Iteration and Feedback Rules

- The model MUST make modifications if the user requests changes to the requirements
- The model MUST incorporate all user feedback before proceeding to the design phase
- The model MUST offer to return to requirements if gaps are identified during design
- The model MUST ensure all five technical areas are comprehensively covered before completion

## Phase Completion

This requirements document represents Phase 1 of the Feature Requirements-First workflow. After user approval, the workflow will proceed to Phase 2 (Design Document Creation) where detailed technical specifications will be extracted and organized into patent-ready documentation format.
