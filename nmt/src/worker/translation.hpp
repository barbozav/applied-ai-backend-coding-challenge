#ifndef _TRANSLATION_HPP_
#define _TRANSLATION_HPP_

#include <string>

#include <nlohmann/json.hpp>


using json = nlohmann::json;


class Translation {
public:
  
  Translation(json aRequest);
  
  ~Translation() {};
  
  void run();
  
  inline std::string getString() { return mPayload.dump(); };
  
  inline const char *getCallbackUrl() { return mCallbackUrl.c_str(); };

private:
  
  std::string mId;
  std::string mText;
  std::string mSourceLanguage;
  std::string mTargetLanguage;
  std::string mTranslatedText;
  std::string mCallbackUrl;
  std::string mStatus;
  
  json mPayload;
};

#endif
