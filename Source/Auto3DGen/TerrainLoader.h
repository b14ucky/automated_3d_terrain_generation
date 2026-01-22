// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "TerrainLoader.generated.h"

USTRUCT(BlueprintType)
struct FTerrainConfig {
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 XSize;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 YSize;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float Scale;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float ZMultiplier;

	UPROPERTY(EditAnywhere, BLueprintReadWrite)
	float UVScale;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<float> Heightmap;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<int32> VegetationMap;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bWaterOn;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float WaterHeight;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bFogOn;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float FogDensity;
};
/**
 * 
 */
UCLASS()
class AUTO3DGEN_API UTerrainLoader : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()
	
public:
	UFUNCTION(BlueprintCallable, Category = "Terrain")
	static bool LoadTerrainConfig(FTerrainConfig& OutConfig);
	static FString ReadFile(FString FilePath);
};
