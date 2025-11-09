// Fill out your copyright notice in the Description page of Project Settings.


#include "TerrainLoader.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "JsonObjectConverter.h"

bool UTerrainLoader::LoadTerrainConfig(FTerrainConfig& OutConfig)
{
    FString Filename = "config.json";
    FString FilePath = FPaths::ProjectDir() + Filename;
    FString JsonString;

    if (FFileHelper::LoadFileToString(JsonString, *FilePath)) {
        return FJsonObjectConverter::JsonObjectStringToUStruct<FTerrainConfig>(JsonString, &OutConfig, 0, 0);
    }

    UE_LOG(LogTemp, Error, TEXT("Config file not found: %s"), *FilePath);
    return false;
}

FString UTerrainLoader::ReadFile(FString FilePath)
{
    if (!FPlatformFileManager::Get().GetPlatformFile().FileExists(*FilePath)) {
        return "";
    }

    FString FileContent = "";

    if (!FFileHelper::LoadFileToString(FileContent, *FilePath)) {
        return "";
    }

    return FileContent;
}
