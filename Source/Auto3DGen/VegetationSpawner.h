// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VegetationSpawner.generated.h"

UCLASS()
class AUTO3DGEN_API AVegetationSpawner : public AActor
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	AVegetationSpawner();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Vegetation")
	UStaticMesh* TreeMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Vegetation")
	UMaterialInterface* TreeMaterial;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Vegetation")
	class UInstancedStaticMeshComponent* TreeISM;

	UFUNCTION(BlueprintCallable, Category = "Vegetation")
	void SpawnVegetation(
		int32 XSize,
		int32 YSize,
		float Scale,
		float ZMultiplier,
		const TArray<float>& Heightmap,
		const TArray<int32>& VegetationMap
	);

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

};
