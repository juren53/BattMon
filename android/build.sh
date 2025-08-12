#!/bin/bash

# Battery Monitor Build Script
# This script builds the Battery Monitor Android app

echo "========================================"
echo "Battery Monitor - Build Script"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check for required dependencies
echo -e "\n${YELLOW}Checking dependencies...${NC}"

# Check for Java
if command -v java >/dev/null 2>&1; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    echo -e "${GREEN}✓ Java found: $JAVA_VERSION${NC}"
else
    echo -e "${RED}✗ Java is not installed. Please install Java 8 or higher.${NC}"
    exit 1
fi

# Check for Gradle
if command -v gradle >/dev/null 2>&1; then
    GRADLE_VERSION=$(gradle --version | grep "Gradle" | head -n 1 | cut -d' ' -f2)
    echo -e "${GREEN}✓ Gradle found: $GRADLE_VERSION${NC}"
else
    echo -e "${RED}✗ Gradle is not installed. Please install Gradle.${NC}"
    exit 1
fi

# Check for Android SDK
ANDROID_SDK_PATH="$HOME/Android/Sdk"
if [ -d "$ANDROID_SDK_PATH" ]; then
    echo -e "${GREEN}✓ Android SDK found at: $ANDROID_SDK_PATH${NC}"
else
    echo -e "${RED}✗ Android SDK not found at the default location: $ANDROID_SDK_PATH${NC}"
    echo -e "${YELLOW}  Please make sure Android SDK is installed or set the correct path.${NC}"
    exit 1
fi

# Set Android SDK environment variables if not set
if [ -z "$ANDROID_HOME" ]; then
    export ANDROID_HOME="$ANDROID_SDK_PATH"
    echo -e "${YELLOW}Set ANDROID_HOME to $ANDROID_HOME${NC}"
fi

if [ -z "$ANDROID_SDK_ROOT" ]; then
    export ANDROID_SDK_ROOT="$ANDROID_SDK_PATH"
    echo -e "${YELLOW}Set ANDROID_SDK_ROOT to $ANDROID_SDK_ROOT${NC}"
fi

# Build the project
echo -e "\n${YELLOW}Building the project...${NC}"
cd "$(dirname "$0")"

# Clean the project first
echo -e "${YELLOW}Cleaning the project...${NC}"
if gradle clean; then
    echo -e "${GREEN}Clean successful${NC}"
else
    echo -e "${RED}Clean failed${NC}"
    exit 1
fi

# Build the debug APK
echo -e "${YELLOW}Building debug APK...${NC}"
if gradle assembleDebug; then
    echo -e "${GREEN}Build successful${NC}"
else
    echo -e "${RED}Build failed${NC}"
    exit 1
fi

# Check if APK was generated
APK_PATH="./app/build/outputs/apk/debug/app-debug.apk"
if [ -f "$APK_PATH" ]; then
    echo -e "\n${GREEN}APK generated successfully at:${NC}"
    echo -e "${YELLOW}$PWD/$APK_PATH${NC}"
    
    echo -e "\n${YELLOW}Installation instructions:${NC}"
    echo -e "1. Connect your Android device via USB"
    echo -e "2. Make sure USB debugging is enabled on your device"
    echo -e "3. Run the following command to install the app:"
    echo -e "   ${GREEN}adb install -r $PWD/$APK_PATH${NC}"
    echo -e "\nOr open the project in Android Studio and run it directly on your device."
else
    echo -e "\n${RED}APK not found. Build might have failed.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Build process completed!${NC}"

