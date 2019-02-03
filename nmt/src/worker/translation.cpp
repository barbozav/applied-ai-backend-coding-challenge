#include <string>

#include "worker/translation.hpp"

#include <iostream>

Translation::Translation(json aRequest) {
  mPayload        = aRequest;
  mText           = mPayload["text"];
  mSourceLanguage = mPayload["source_language"];
  mTargetLanguage = mPayload["target_language"];
  mTranslatedText = "";
  mCallbackUrl    = mPayload["callback_url"];
  mStatus         = "new";
}

void Translation::run() {
  mTranslatedText = "Hola!";
  // Call Marian-NMT server here instead.
  mStatus = "completed";

  mPayload["translated_text"] = mTranslatedText;
  mPayload["status"] = mStatus;
}
