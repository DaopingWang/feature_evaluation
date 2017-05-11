/**
 * Created by Wang.Daoping on 04.05.2017.
 */
public class Feature {
    private String name;
    private String value;
    private float completeness;

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

    public void setCompleteness(float completeness){
        this.completeness = completeness;
    }

    public float getCompleteness(){
        return this.completeness;
    }

    @Override public boolean equals(Object o){
        if(o instanceof Feature)
            return ((Feature) o).getName().equals(this.getName());
        if(o instanceof String)
            return (this.getName().equals(o));
        return false;
    }
}
