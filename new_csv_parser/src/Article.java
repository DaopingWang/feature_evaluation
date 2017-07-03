import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;


class Article {
    String articleID;
    HashMap<String, String> features;
    List<Float> priceList;
    Article(String articleID){
        this.articleID = articleID;
        this.features = new HashMap<>();
        this.priceList = new ArrayList<>();
    }

    void addFeature(String featureName, String featureValue){
        // if(this.features.containsKey(featureName)) System.out.println("addFeature: duplicate feature");
        this.features.put(featureName, featureValue);
    }

    void addPrice(float price){
        if(price == -1) return;
        this.priceList.add(price);
    }

    float getAvgPrice(){
        float sum = 0;
        int priceCount = priceList.size();
        if(priceCount == 0) return -1;
        for(float price : priceList){
            sum += price;
        }
        return sum / priceCount;
    }
}
