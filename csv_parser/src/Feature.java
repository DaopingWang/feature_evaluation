/**
 * Created by Wang.Daoping on 04.05.2017.
 */
public class Feature {
    private String name;
    private String value;

    public Feature(String name){
        this.name = name;
    }

    public Feature(String name, String value){
        this.name = name;
        this.value = value;
    }

    public String getName(){
        return name;
    }

    public String getValue(){
        return value;
    }
}
