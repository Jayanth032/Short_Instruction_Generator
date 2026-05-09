from core.analyzer import analyze_image

# 🔥 Your test images (FIXED PATHS)
image_paths = [
    "test_images/test9.jpeg",
    "test_images/test10.jpeg",
    "test_images/test8.jpeg",
    "test_images/test7.jpeg"
]

# 🔥 Actual answers (FIXED)
ground_truth = [
    "fan",
    "Shirt",
    "bottle",
    "luggage"
]


def evaluate_accuracy(image_paths, ground_truth):

    correct = 0
    partial = 0

    for i in range(len(image_paths)):

        result = analyze_image(image_paths[i])

        if result is None or "error" in result:
            print(f"Error in image {i+1}")
            continue

        predicted = result.get("product_name", "").lower().strip()
        actual = ground_truth[i].lower().strip()

        print(f"\nImage {i+1}")
        print("Actual:", actual)
        print("Predicted:", predicted)

        # 🔥 Improved matching
        if actual in predicted:
            correct += 1

        elif any(word in predicted for word in actual.split()):
            partial += 1

    total = len(image_paths)

    accuracy = ((correct + 0.5 * partial) / total) * 100

    print("\nFinal Results:")
    print("Correct:", correct)
    print("Partial:", partial)
    print("Total:", total)
    print("Accuracy:", round(accuracy, 2), "%")

    return accuracy


# Run evaluation
evaluate_accuracy(image_paths, ground_truth)