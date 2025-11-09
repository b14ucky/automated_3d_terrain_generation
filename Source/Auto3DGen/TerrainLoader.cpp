// Fill out your copyright notice in the Description page of Project Settings.


#include "TerrainLoader.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"

TArray<float> UTerrainLoader::LoadHeightmap(int width, int height) 
{
    TArray<FString> Lines;
    FString Filename = "heightmap.csv";
    FString FilePath = FPaths::ProjectDir() + Filename;
    FFileHelper::LoadFileToStringArray(Lines, *FilePath);

    TArray<float> Heightmap;

    // allocate memory for the array so Unreal
    // does not have to relocate every now and then
    Heightmap.Reserve(width * height);

    for (FString& line : Lines) {
        TArray<FString> Parts;
        line.ParseIntoArray(Parts, TEXT(","));

        for (FString& part : Parts) {
            Heightmap.Add(FCString::Atof(*part));
            UE_LOG(LogTemp, Warning, TEXT("Value: %f"), FCString::Atof(*part));
        }
    }

    return Heightmap;
}
