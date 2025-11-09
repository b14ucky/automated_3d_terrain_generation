// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "TerrainLoader.generated.h"

/**
 * 
 */
UCLASS()
class AUTO3DGEN_API UTerrainLoader : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()
	
public:
	UFUNCTION(BlueprintCallable, Category = "Terrain")
	static TArray<float> LoadHeightmap(int width, int height);
};
