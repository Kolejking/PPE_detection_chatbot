from pathlib import Path

from ultralytics import YOLO

from src.ppe_association import (
    extract_detections,
    split_detections,
    calculate_association_score,
    associate_ppe_to_persons,
    build_ppe_status,
    MIN_ASSOCIATION_SCORE,
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "models/best1.pt"
IMAGE_DIR = Path("inputs/images")

CONFIDENCE = 0.25


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("GOGGLE ASSOCIATION DIAGNOSTIC")
    print("=" * 70)

    print(f"Model              : {MODEL_PATH}")
    print(f"Image directory     : {IMAGE_DIR}")
    print(f"YOLO confidence     : {CONFIDENCE}")
    print(f"Minimum assoc. score: {MIN_ASSOCIATION_SCORE}")

    print("=" * 70)

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = YOLO(MODEL_PATH)

    print("\nModel loaded successfully.")
    print("Classes:")
    print(model.names)

    # --------------------------------------------------------
    # Find images
    # --------------------------------------------------------

    image_files = list(IMAGE_DIR.glob("*"))

    print(f"\nImages found: {len(image_files)}")

    positive_goggles_found = 0

    # --------------------------------------------------------
    # Process every image
    # --------------------------------------------------------

    for image_path in image_files:

        if not image_path.is_file():
            continue

        results = model.predict(
            source=str(image_path),
            conf=CONFIDENCE,
            verbose=False
        )

        if not results:
            continue

        result = results[0]

        # ----------------------------------------------------
        # Convert YOLO result into project detection format
        # ----------------------------------------------------

        detections = extract_detections(
            result,
            model.names
        )

        # ----------------------------------------------------
        # Split detections into PPE categories
        # ----------------------------------------------------

        (
            persons,
            helmets,
            no_helmets,
            vests,
            no_vests,
            safety_shoes,
            no_safety_shoes,
            without_safety_goggles,
            with_safety_goggles,
        ) = split_detections(detections)

        # ----------------------------------------------------
        # Only investigate images containing positive goggles
        # ----------------------------------------------------

        if not with_safety_goggles:
            continue

        positive_goggles_found += len(with_safety_goggles)

        print("\n")
        print("#" * 70)
        print(f"IMAGE: {image_path}")
        print("#" * 70)

        print(f"Persons detected              : {len(persons)}")
        print(
            f"With-Safety-Goggles detected  : "
            f"{len(with_safety_goggles)}"
        )

        # ====================================================
        # PART 1: RAW ASSOCIATION SCORE
        # ====================================================

        print("\n")
        print("=" * 70)
        print("RAW ASSOCIATION SCORE CHECK")
        print("=" * 70)

        for goggles_index, goggles in enumerate(
            with_safety_goggles,
            start=1
        ):

            print("\n")
            print("-" * 70)
            print(
                f"WITH-SAFETY-GOGGLES #{goggles_index}"
            )
            print("-" * 70)

            print(
                "Goggles confidence:",
                round(
                    float(
                        goggles.get(
                            "confidence",
                            0.0
                        )
                    ),
                    4
                )
            )

            print(
                "Goggles box:",
                goggles.get("box")
            )

            if not persons:

                print(
                    "NO PERSON DETECTED IN THIS IMAGE."
                )

                continue

            # ------------------------------------------------
            # Compare goggles against every person
            # ------------------------------------------------

            for person_index, person in enumerate(
                persons,
                start=1
            ):

                metrics = calculate_association_score(
                    goggles,
                    person,
                    "goggles"
                )

                print()
                print(
                    f"Person #{person_index}"
                )

                print(
                    "Person box:",
                    person.get("box")
                )

                print(
                    "Overlap      :",
                    round(
                        metrics["overlap"],
                        4
                    )
                )

                print(
                    "Position     :",
                    round(
                        metrics["position"],
                        4
                    )
                )

                print(
                    "Distance     :",
                    round(
                        metrics["distance"],
                        4
                    )
                )

                print(
                    "Confidence   :",
                    round(
                        metrics["confidence"],
                        4
                    )
                )

                print(
                    "Spatial valid:",
                    metrics["spatial_valid"]
                )

                print(
                    "FINAL SCORE  :",
                    round(
                        metrics["final"],
                        4
                    )
                )

                if (
                    metrics["final"]
                    >= MIN_ASSOCIATION_SCORE
                ):

                    print(
                        "RESULT       : "
                        "✅ ASSOCIATION PASSES"
                    )

                else:

                    print(
                        "RESULT       : "
                        "❌ ASSOCIATION FAILS"
                    )

        # ====================================================
        # PART 2: ACTUAL ASSOCIATION FUNCTION
        # ====================================================

        print("\n")
        print("=" * 70)
        print("RAW ASSOCIATION FUNCTION RESULT")
        print("=" * 70)

        associations = associate_ppe_to_persons(
            persons=persons,
            helmets=helmets,
            no_helmets=no_helmets,
            vests=vests,
            no_vests=no_vests,
            safety_shoes=safety_shoes,
            no_safety_shoes=no_safety_shoes,
            without_safety_goggles=without_safety_goggles,
            with_safety_goggles=with_safety_goggles,
            min_score=MIN_ASSOCIATION_SCORE,
        )

        # ----------------------------------------------------
        # Print raw association records
        # ----------------------------------------------------

        for record in associations:

            print("\n")
            print(
                f"Person {record['person_index']}"
            )

            print(
                "With goggles:",
                record.get(
                    "with_safety_goggles"
                )
            )

            print(
                "With goggles score:",
                record.get(
                    "with_safety_goggles_score"
                )
            )

            print(
                "With goggles metrics:",
                record.get(
                    "with_safety_goggles_metrics"
                )
            )

            print(
                "Without goggles:",
                record.get(
                    "without_safety_goggles"
                )
            )

            print(
                "Without goggles score:",
                record.get(
                    "without_safety_goggles_score"
                )
            )

        # ====================================================
        # PART 3: BUILD FINAL PPE STATUS
        # ====================================================

        statuses = build_ppe_status(
            associations
        )

        print("\n")
        print("=" * 70)
        print("FINAL PPE STATUS")
        print("=" * 70)

        for status in statuses:

            print("\n")
            print(
                f"Person {status['person_index']}"
            )

            print(
                "Goggles status:",
                status.get(
                    "goggles_status"
                )
            )

            print(
                "Safety goggles status:",
                status.get(
                    "safety_goggles_status"
                )
            )

            print(
                "Overall status:",
                status.get(
                    "overall_status"
                )
            )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")
    print("=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    print(
        "Total positive goggles detections:",
        positive_goggles_found
    )

    print(
        "Minimum association score:",
        MIN_ASSOCIATION_SCORE
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
    