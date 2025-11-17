// Fill out your copyright notice in the Description page of Project Settings.


#include "VegetationSpawner.h"
#include "Components/InstancedStaticMeshComponent.h"

// Sets default values
AVegetationSpawner::AVegetationSpawner()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

	TreeISM = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("TreeISM"));
	SetRootComponent(TreeISM);
}

void AVegetationSpawner::SpawnVegetation(int32 XSize, int32 YSize, float Scale, float ZMultiplier, const TArray<float>& Heightmap, const TArray<int32>& VegetationMap)
{
	if (!TreeMesh) {
		UE_LOG(LogTemp, Error, TEXT("TreeMesh is not set!"));
		return;
	}

	TreeISM->ClearInstances();
	TreeISM->SetStaticMesh(TreeMesh);

	if (TreeMaterial) {
		TreeISM->SetMaterial(0, TreeMaterial);
	}

	for (int X = 0; X < XSize; ++X) {
		for (int Y = 0; Y < YSize; ++Y) {
			int index = Y * XSize + X;

			if (VegetationMap[index] == 0) continue;

			float Z = Heightmap[index] * ZMultiplier;

			FVector Position(X * Scale, Y * Scale, Z);

			FRotator RandomRotation = FRotator(0, FMath::FRandRange(0.0f, 360.0f), 0);

			float Scale = FMath::FRandRange(0.6f, 1.0f);
			FVector RandomScale(Scale);

			// TODO: Fix forest generation algorithm (add space of radius R between trees)
			// to correctly place trees on uneven terrain
			/*FVector Start(Position.X, Position.Y, 10'000.f);
			FVector End(Position.X, Position.Y, 0.f);
			FHitResult HitResult;

			if (GetWorld()->LineTraceSingleByChannel(HitResult, Start, End, ECC_WorldStatic)) {
				FVector CorrectedPosition = HitResult.ImpactPoint;
				FTransform InstanceTransform(RandomRotation, CorrectedPosition, RandomScale);
				TreeISM->AddInstance(InstanceTransform);
			}*/

			FTransform InstanceTransform(RandomRotation, Position, RandomScale);
			TreeISM->AddInstance(InstanceTransform);
		}
	}
}

// Called when the game starts or when spawned
void AVegetationSpawner::BeginPlay()
{
	Super::BeginPlay();
	
}

// Called every frame
void AVegetationSpawner::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

